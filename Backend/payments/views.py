import os
import json
import hmac
import hashlib
import logging
from decimal import Decimal
from io import BytesIO
from typing import Any, cast

import razorpay
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Donation
from .serializers import DonationCreateSerializer, DonationSerializer, DonationVerifySerializer


logger = logging.getLogger(__name__)

ORDER_RATE_LIMIT_COUNT = int(os.environ.get('PAYMENTS_ORDER_RATE_LIMIT_COUNT', '20'))
ORDER_RATE_LIMIT_WINDOW = int(os.environ.get('PAYMENTS_ORDER_RATE_LIMIT_WINDOW_SECONDS', '3600'))
VERIFY_RATE_LIMIT_COUNT = int(os.environ.get('PAYMENTS_VERIFY_RATE_LIMIT_COUNT', '60'))
VERIFY_RATE_LIMIT_WINDOW = int(os.environ.get('PAYMENTS_VERIFY_RATE_LIMIT_WINDOW_SECONDS', '3600'))
WEBHOOK_RATE_LIMIT_COUNT = int(os.environ.get('PAYMENTS_WEBHOOK_RATE_LIMIT_COUNT', '240'))
WEBHOOK_RATE_LIMIT_WINDOW = int(os.environ.get('PAYMENTS_WEBHOOK_RATE_LIMIT_WINDOW_SECONDS', '3600'))


def _request_key(request):
    forwarded_for = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
    ip = forwarded_for or (request.META.get('REMOTE_ADDR') or 'unknown')
    if getattr(request.user, 'is_authenticated', False):
        return f'user:{request.user.id}:{ip}'
    return f'anon:{ip}'


def _rate_limit_or_none(request, scope, limit_count, window_seconds):
    key = f'payments:rl:{scope}:{_request_key(request)}'
    now = int(timezone.now().timestamp())
    bucket = cache.get(key) or {'count': 0, 'start': now}

    elapsed = now - int(bucket.get('start', now))
    if elapsed >= window_seconds:
        bucket = {'count': 0, 'start': now}

    bucket['count'] = int(bucket.get('count', 0)) + 1
    cache.set(key, bucket, timeout=window_seconds)

    if bucket['count'] > limit_count:
        retry_after = max(1, window_seconds - (now - int(bucket['start'])))
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={'Retry-After': str(retry_after)},
        )
    return None


def _is_treasurer(user):
    if not getattr(user, 'is_authenticated', False):
        return False

    try:
        member = getattr(user, 'member', None)
        if member and (member.committee_role or '').strip().lower() == 'treasurer':
            return True
    except Exception:
        pass

    try:
        for entry in user.committee_entries.all():
            if (entry.role or '').strip().lower() == 'treasurer':
                return True
    except Exception:
        pass

    return (getattr(user, 'role', '') or '').strip().lower() == 'treasurer'


def _get_razorpay_keys():
    key_id = os.environ.get('RAZORPAY_KEY_ID', '').strip()
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET', '').strip()
    if not key_id or not key_secret:
        return None, None
    return key_id, key_secret


def _get_razorpay_client():
    key_id, key_secret = _get_razorpay_keys()
    if not key_id or not key_secret:
        return None
    return razorpay.Client(auth=(key_id, key_secret))


def _next_receipt_number():
    today = timezone.localdate()
    prefix = f"KFA-{today.strftime('%Y%m%d')}"
    last = Donation.objects.filter(receipt_number__startswith=prefix).order_by('-receipt_number').first()
    if not last or not last.receipt_number:
        return f"{prefix}-001"

    try:
        current_num = int(last.receipt_number.rsplit('-', 1)[-1])
    except Exception:
        current_num = 0
    return f"{prefix}-{current_num + 1:03d}"


def _build_receipt_pdf(donation):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin_x = 18 * mm
    content_width = width - (2 * margin_x)

    # Header band
    pdf.setFillColor(colors.HexColor('#1B3D3A'))
    pdf.roundRect(margin_x, height - 50 * mm, content_width, 34 * mm, 4 * mm, fill=1, stroke=0)

    # Brand title
    y = height - 26 * mm
    pdf.setTitle(f"Donation Receipt {donation.receipt_number}")

    pdf.setFillColor(colors.white)
    pdf.setFont('Helvetica-Bold', 17)
    pdf.drawString(margin_x + 6 * mm, y, 'Kollamparambil Family Association')

    y -= 8 * mm
    pdf.setFont('Helvetica', 10.5)
    pdf.drawString(margin_x + 6 * mm, y, 'Digital Donation Receipt')

    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawRightString(width - margin_x - 6 * mm, height - 26 * mm, f"Receipt: {donation.receipt_number}")
    pdf.setFont('Helvetica', 9.5)
    pdf.drawRightString(
        width - margin_x - 6 * mm,
        height - 34 * mm,
        timezone.localtime(donation.paid_at or donation.created_at).strftime('%Y-%m-%d %H:%M:%S'),
    )

    # Details panel
    panel_top = height - 58 * mm
    panel_height = 95 * mm
    pdf.setFillColor(colors.HexColor('#F7FAFC'))
    pdf.roundRect(margin_x, panel_top - panel_height, content_width, panel_height, 3 * mm, fill=1, stroke=0)

    rows = [
        ('Donor Name', donation.donor_name),
        ('Donor Email', donation.donor_email or '-'),
        ('Donor Phone', donation.donor_phone or '-'),
        ('Purpose', donation.purpose or 'General Donation'),
        ('Payment ID', donation.razorpay_payment_id or '-'),
        ('Order ID', donation.razorpay_order_id),
    ]

    row_y = panel_top - 10 * mm
    for label, value in rows:
        pdf.setFillColor(colors.HexColor('#64748B'))
        pdf.setFont('Helvetica-Bold', 9)
        pdf.drawString(margin_x + 6 * mm, row_y, label)

        pdf.setFillColor(colors.HexColor('#0F172A'))
        pdf.setFont('Helvetica', 10.2)
        pdf.drawString(margin_x + 45 * mm, row_y, str(value))
        row_y -= 12 * mm

    # Amount highlight
    amount_box_y = panel_top - panel_height - 18 * mm
    pdf.setFillColor(colors.HexColor('#FFF7ED'))
    pdf.roundRect(margin_x, amount_box_y, content_width, 14 * mm, 3 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor('#9A3412'))
    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(margin_x + 6 * mm, amount_box_y + 5 * mm, 'Total Donation Amount')
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawRightString(width - margin_x - 6 * mm, amount_box_y + 5 * mm, f"INR {donation.amount}")

    # Footer note
    footer_y = amount_box_y - 20 * mm
    pdf.setStrokeColor(colors.HexColor('#E2E8F0'))
    pdf.line(margin_x, footer_y + 10 * mm, width - margin_x, footer_y + 10 * mm)
    pdf.setFillColor(colors.HexColor('#475569'))
    pdf.setFont('Helvetica-Oblique', 9.5)
    pdf.drawString(margin_x, footer_y + 3 * mm, 'This is a computer-generated receipt for the donation received by KFA.')
    pdf.drawString(margin_x, footer_y - 2 * mm, 'Thank you for your contribution and continued support.')

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


def _mark_donation_paid(donation, payment_id=None, signature=None):
    if donation.status == 'paid':
        return donation

    donation.status = 'paid'
    if payment_id:
        donation.razorpay_payment_id = payment_id
    if signature:
        donation.razorpay_signature = signature
    donation.paid_at = timezone.now()
    donation.receipt_number = donation.receipt_number or _next_receipt_number()
    donation.ensure_receipt_token()

    receipt_bytes = _build_receipt_pdf(donation)
    file_name = f"receipt-{donation.receipt_number}.pdf"
    donation.receipt_pdf.save(file_name, ContentFile(receipt_bytes.read()), save=False)
    donation.save()
    return donation


def _webhook_signature_is_valid(raw_body, signature_header):
    secret = (os.environ.get('RAZORPAY_WEBHOOK_SECRET') or '').strip()
    if not secret:
        logger.warning('Razorpay webhook secret is not configured.')
        return False

    if not signature_header:
        return False

    digest = hmac.new(
        key=secret.encode('utf-8'),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, signature_header)


class DonationOrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not _is_treasurer(request.user):
            return Response(
                {'error': 'Only treasurer can create donation payment requests.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        throttled = _rate_limit_or_none(request, 'create-order', ORDER_RATE_LIMIT_COUNT, ORDER_RATE_LIMIT_WINDOW)
        if throttled:
            return throttled

        serializer = DonationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, Any], serializer.validated_data)

        client = _get_razorpay_client()
        key_id, _ = _get_razorpay_keys()
        if not client or not key_id:
            return Response(
                {'error': 'Razorpay is not configured on server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        amount = payload['amount']
        amount_paise = int((amount * Decimal('100')).quantize(Decimal('1')))

        order = client.order.create(  # type: ignore[attr-defined]
            {
                'amount': amount_paise,
                'currency': 'INR',
                'payment_capture': 1,
                'notes': {
                    'purpose': payload.get('purpose') or 'General Donation',
                    'donor_name': payload['donor_name'],
                },
            }
        )

        member = getattr(request.user, 'member', None) if getattr(request.user, 'is_authenticated', False) else None

        donation = Donation.objects.create(
            donor_user=request.user if getattr(request.user, 'is_authenticated', False) else None,
            donor_member=member,
            donor_name=payload['donor_name'],
            donor_email=payload.get('donor_email') or None,
            donor_phone=payload.get('donor_phone') or None,
            purpose=payload.get('purpose') or None,
            amount=amount,
            currency='INR',
            razorpay_order_id=order['id'],
            status='pending',
        )

        return Response(
            {
                'public_id': str(donation.public_id),
                'order_id': order['id'],
                'amount': amount,
                'amount_paise': amount_paise,
                'currency': 'INR',
                'key_id': key_id,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'donor_phone': donation.donor_phone,
                'purpose': donation.purpose,
            },
            status=status.HTTP_201_CREATED,
        )


class DonationVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        throttled = _rate_limit_or_none(request, 'verify', VERIFY_RATE_LIMIT_COUNT, VERIFY_RATE_LIMIT_WINDOW)
        if throttled:
            return throttled

        serializer = DonationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, Any], serializer.validated_data)

        client = _get_razorpay_client()
        if not client:
            return Response(
                {'error': 'Razorpay is not configured on server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        donation = Donation.objects.filter(razorpay_order_id=payload['razorpay_order_id']).first()
        if not donation:
            return Response({'error': 'Donation order not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            client.utility.verify_payment_signature(  # type: ignore[attr-defined]
                {
                    'razorpay_order_id': payload['razorpay_order_id'],
                    'razorpay_payment_id': payload['razorpay_payment_id'],
                    'razorpay_signature': payload['razorpay_signature'],
                }
            )
        except Exception:
            donation.status = 'failed'
            donation.save(update_fields=['status', 'updated_at'])
            return Response({'error': 'Invalid payment signature.'}, status=status.HTTP_400_BAD_REQUEST)

        if donation.status == 'paid' and donation.razorpay_payment_id and donation.razorpay_payment_id != payload['razorpay_payment_id']:
            return Response({'error': 'Order already verified with a different payment id.'}, status=status.HTTP_409_CONFLICT)

        donation = _mark_donation_paid(
            donation,
            payment_id=payload['razorpay_payment_id'],
            signature=payload['razorpay_signature'],
        )

        receipt_url = None
        if donation.receipt_pdf:
            receipt_url = request.build_absolute_uri(f"/api/payments/receipt/{donation.public_id}/?token={donation.receipt_token}")

        return Response(
            {
                'status': donation.status,
                'receipt_number': donation.receipt_number,
                'receipt_url': receipt_url,
                'public_id': str(donation.public_id),
                'receipt_token': donation.receipt_token,
            },
            status=status.HTTP_200_OK,
        )


class DonationReceiptDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, public_id):
        donation = Donation.objects.filter(public_id=public_id, status='paid').first()
        if not donation or not donation.receipt_pdf:
            raise Http404('Receipt not found.')

        token = (request.query_params.get('token') or '').strip()
        is_owner = bool(
            getattr(request.user, 'is_authenticated', False)
            and donation.donor_user
            and donation.donor_user.id == request.user.id
        )

        if not is_owner and (not token or token != donation.receipt_token):
            raise Http404('Receipt not found.')

        return FileResponse(
            donation.receipt_pdf.open('rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f"{donation.receipt_number or 'donation-receipt'}.pdf",
        )


class DonationMyHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        donations = Donation.objects.filter(donor_user=request.user)
        return Response(DonationSerializer(donations, many=True, context={'request': request}).data)


class RazorpayWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        throttled = _rate_limit_or_none(request, 'webhook', WEBHOOK_RATE_LIMIT_COUNT, WEBHOOK_RATE_LIMIT_WINDOW)
        if throttled:
            return throttled

        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        raw_body = request.body or b''
        if not _webhook_signature_is_valid(raw_body, signature):
            return Response({'error': 'Invalid webhook signature.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except Exception:
            return Response({'error': 'Invalid webhook payload.'}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get('event')
        entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
        order_id = entity.get('order_id')
        payment_id = entity.get('id')

        if not order_id:
            return Response({'status': 'ignored', 'reason': 'missing_order_id'}, status=status.HTTP_200_OK)

        donation = Donation.objects.filter(razorpay_order_id=order_id).first()
        if not donation:
            return Response({'status': 'ignored', 'reason': 'donation_not_found'}, status=status.HTTP_200_OK)

        if event in {'payment.captured', 'order.paid'}:
            _mark_donation_paid(donation, payment_id=payment_id)
            return Response({'status': 'processed'}, status=status.HTTP_200_OK)

        if event in {'payment.failed'}:
            if donation.status != 'paid':
                donation.status = 'failed'
                donation.save(update_fields=['status', 'updated_at'])
            return Response({'status': 'processed'}, status=status.HTTP_200_OK)

        return Response({'status': 'ignored', 'event': event}, status=status.HTTP_200_OK)
