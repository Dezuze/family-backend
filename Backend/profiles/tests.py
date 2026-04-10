from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from families.models import Family, FamilyMember
from profiles.models import Committee, CommunityRole

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


class CommunityRoleApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='role_admin',
            email='role_admin@example.com',
            password='pass1234',
        )

    def test_public_list_returns_predefined_roles(self):
        res = self.client.get('/api/profiles/community-roles/')
        self.assertEqual(res.status_code, 200)
        role_names = [row['name'] for row in res.data]
        self.assertIn('President', role_names)
        self.assertIn('Treasurer', role_names)

    def test_create_role_requires_auth(self):
        res = self.client.post(
            '/api/profiles/community-roles/',
            {'name': 'Youth Coordinator', 'priority': 15},
            format='json',
        )
        self.assertIn(res.status_code, [401, 403])

    def test_authenticated_user_can_add_role(self):
        self.client.force_authenticate(self.user)
        res = self.client.post(
            '/api/profiles/community-roles/',
            {'name': 'Youth Coordinator', 'priority': 15},
            format='json',
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(CommunityRole.objects.filter(name='Youth Coordinator').exists())
