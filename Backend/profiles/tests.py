from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from families.models import Family, FamilyMember
from profiles.models import Committee

User = get_user_model()


class CommitteePublicViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family = Family.objects.create(sl_no='1', branch='Main', member_no='P100')
        self.member = FamilyMember.objects.create(
            family=self.family,
            name='Committee User',
            relation='Head',
            committee_role='Treasurer',
        )
        self.user = User.objects.create_user(
            username='committee_user',
            email='committee@example.com',
            password='pass1234',
            member=self.member,
        )
        Committee.objects.create(user=self.user, role='Secretary')

    def test_public_committee_list_hides_sensitive_fields(self):
        res = self.client.get('/api/profiles/committee/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        row = res.data[0]
        self.assertIn('name', row)
        self.assertIn('role', row)
        self.assertNotIn('phone_no', row)
        self.assertNotIn('user', row)

    def test_member_committee_role_overrides_entry_role(self):
        res = self.client.get('/api/profiles/committee/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]['role'], 'Treasurer')

    def test_committee_create_requires_auth(self):
        payload = {'user': self.user.id, 'role': 'President'}
        unauth = self.client.post('/api/profiles/committee/', payload, format='json')
        self.assertIn(unauth.status_code, [401, 403])
