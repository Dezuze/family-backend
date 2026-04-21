from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from families.models import Family, FamilyMember
from profiles.models import CommunityRole

User = get_user_model()


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
