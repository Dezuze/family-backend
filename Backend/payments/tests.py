from decimal import Decimal
from unittest.mock import patch
import json
import hmac
import hashlib

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test import TestCase
from rest_framework.test import APIClient

from families.models import Family, FamilyMember
from payments.models import Donation

User = get_user_model()


class PaymentsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no='1', branch='Main', member_no='F100')
        self.member = FamilyMember.objects.create(
            family=self.family,
            name='Donor Member',
            relation='Head',
            age=40,
            blood_group='O+',
            committee_role='Treasurer',
        )
        self.user = User.objects.create_user(
            username='donor',
            email='donor@example.com',
            password='pass1234',
            member=self.member,
        )

    @patch('payments.views._get_razorpay_client', return_value=None)
    def test_create_order_requires_razorpay_config(self, _mock_client):
        self.client.force_login(self.user)
        payload = {
            'donor_name': 'Test Donor',
            'amount': '150.00',
        }
        response = self.client.post('/api/payments/create-order/', payload, format='json')
        self.assertEqual(response.status_code, 503)

    def test_create_order_rejects_non_treasurer(self):
        other_member = FamilyMember.objects.create(
            family=self.family,
            name='Regular Member',
            relation='Member',
            age=29,
            blood_group='A+',
        )
        other_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='pass1234',
            member=other_member,
        )
        self.client.force_login(other_user)

        payload = {
            'donor_name': 'Test Donor',
            'amount': '150.00',
        }
        response = self.client.post('/api/payments/create-order/', payload, format='json')
        self.assertEqual(response.status_code, 403)

    @patch('payments.views._get_razorpay_keys', return_value=('rzp_test_key', 'rzp_test_secret'))
    @patch('payments.views._get_razorpay_client')
    def test_create_order_persists_pending_donation(self, mock_get_client, _mock_get_keys):
        class FakeOrderApi:
            @staticmethod
            def create(_payload):
                return {'id': 'order_123'}

        class FakeClient:
            order = FakeOrderApi()

        mock_get_client.return_value = FakeClient()

        payload = {
            'donor_name': 'Test Donor',
            'donor_email': 'test@example.com',
            'donor_phone': '9999999999',
            'purpose': 'Temple support',
            'amount': '250.00',
        }
        self.client.force_login(self.user)
        response = self.client.post('/api/payments/create-order/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['order_id'], 'order_123')

        donation = Donation.objects.get(razorpay_order_id='order_123')
        self.assertEqual(donation.status, 'pending')
        self.assertEqual(donation.amount, Decimal('250.00'))

    @patch('payments.views._get_razorpay_client')
    def test_verify_marks_paid_and_generates_receipt(self, mock_get_client):
        donation = Donation.objects.create(
            donor_name='Test Donor',
            amount=Decimal('300.00'),
            currency='INR',
            razorpay_order_id='order_abc',
            status='pending',
            donor_user=self.user,
            donor_member=self.member,
        )

        class FakeUtility:
            @staticmethod
            def verify_payment_signature(_payload):
                return True

        class FakeClient:
            utility = FakeUtility()

        mock_get_client.return_value = FakeClient()

        verify_payload = {
            'razorpay_order_id': 'order_abc',
            'razorpay_payment_id': 'pay_xyz',
            'razorpay_signature': 'signature_ok',
        }

        response = self.client.post('/api/payments/verify/', verify_payload, format='json')
        self.assertEqual(response.status_code, 200)

        donation.refresh_from_db()
        self.assertEqual(donation.status, 'paid')
        self.assertEqual(donation.razorpay_payment_id, 'pay_xyz')
        self.assertTrue(donation.receipt_number)
        self.assertTrue(donation.receipt_pdf)
        self.assertTrue(donation.receipt_token)

    def test_receipt_download_requires_owner_or_token(self):
        donation = Donation.objects.create(
            donor_name='Test Donor',
            amount=Decimal('300.00'),
            currency='INR',
            razorpay_order_id='order_token',
            razorpay_payment_id='pay_token',
            status='paid',
            donor_user=self.user,
            donor_member=self.member,
            receipt_number='KFA-20260405-001',
            receipt_token='secure-token',
        )
        donation.receipt_pdf.save('receipt.pdf', ContentFile(b'pdf-bytes'), save=True)

        no_token_response = self.client.get(f'/api/payments/receipt/{donation.public_id}/')
        self.assertEqual(no_token_response.status_code, 404)

        token_response = self.client.get(f'/api/payments/receipt/{donation.public_id}/?token=secure-token')
        self.assertEqual(token_response.status_code, 200)

    def test_my_donations_includes_receipt_url(self):
        donation = Donation.objects.create(
            donor_name='History Donor',
            amount=Decimal('100.00'),
            currency='INR',
            razorpay_order_id='order_history',
            razorpay_payment_id='pay_history',
            status='paid',
            donor_user=self.user,
            donor_member=self.member,
            receipt_number='KFA-20260405-002',
            receipt_token='history-token',
        )
        donation.receipt_pdf.save('history.pdf', ContentFile(b'pdf-bytes'), save=True)

        self.client.force_login(self.user)
        response = self.client.get('/api/payments/my-donations/')
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body), 1)
        self.assertIn('/api/payments/receipt/', body[0]['receipt_url'])

    @patch('payments.views._get_razorpay_keys', return_value=('rzp_test_key', 'rzp_test_secret'))
    @patch('payments.views._get_razorpay_client')
    def test_create_order_rate_limited(self, mock_get_client, _mock_get_keys):
        class FakeOrderApi:
            @staticmethod
            def create(_payload):
                return {'id': 'order_limit'}

        class FakeClient:
            order = FakeOrderApi()

        mock_get_client.return_value = FakeClient()

        payload = {
            'donor_name': 'Rate Limit Donor',
            'amount': '100.00',
        }

        cache.clear()
        self.client.force_login(self.user)
        with patch('payments.views.ORDER_RATE_LIMIT_COUNT', 1), patch('payments.views.ORDER_RATE_LIMIT_WINDOW', 3600):
            first = self.client.post('/api/payments/create-order/', payload, format='json', HTTP_X_FORWARDED_FOR='203.0.113.51')
            second = self.client.post('/api/payments/create-order/', payload, format='json', HTTP_X_FORWARDED_FOR='203.0.113.51')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)

    @patch.dict('os.environ', {'DONATION_MAX_AMOUNT': '1000.00'})
    def test_create_order_rejects_excessive_amount(self):
        self.client.force_login(self.user)
        payload = {
            'donor_name': 'Huge Donor',
            'amount': '2000.00',
        }
        response = self.client.post('/api/payments/create-order/', payload, format='json')
        self.assertEqual(response.status_code, 400)

    @patch.dict('os.environ', {'RAZORPAY_WEBHOOK_SECRET': 'test-secret'})
    def test_webhook_marks_payment_paid(self):
        donation = Donation.objects.create(
            donor_name='Webhook Donor',
            amount=Decimal('500.00'),
            currency='INR',
            razorpay_order_id='order_webhook',
            status='pending',
        )

        body_dict = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_webhook',
                        'order_id': 'order_webhook',
                    }
                }
            }
        }
        raw = json.dumps(body_dict).encode('utf-8')
        signature = hmac.new(b'test-secret', raw, hashlib.sha256).hexdigest()

        response = self.client.post(
            '/api/payments/webhook/',
            data=raw,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=signature,
        )

        self.assertEqual(response.status_code, 200)
        donation.refresh_from_db()
        self.assertEqual(donation.status, 'paid')
        self.assertEqual(donation.razorpay_payment_id, 'pay_webhook')

    @patch.dict('os.environ', {'RAZORPAY_WEBHOOK_SECRET': 'test-secret'})
    def test_webhook_rejects_invalid_signature(self):
        raw = json.dumps({'event': 'payment.captured'}).encode('utf-8')
        response = self.client.post(
            '/api/payments/webhook/',
            data=raw,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='bad-signature',
        )
        self.assertEqual(response.status_code, 400)
