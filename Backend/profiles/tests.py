from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient


def _make_image_file(name: str = 'test.png') -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new('RGB', (2, 2), color='red').save(buffer, format='PNG')
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type='image/png')


class ProfilesAPITestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='puser', email='p@example.com', member_id='pm1', password='pw')
        self.client = APIClient()

    def test_gallery_create_and_list(self):
        img = _make_image_file('gallery.png')
        resp = self.client.post(
            '/api/profiles/gallery/',
            {'image': img, 'date': '2025-01-01', 'description': 'pic'},
            format='multipart'
        )
        self.assertEqual(resp.status_code, 201, msg=f"resp.data={resp.data}")
        resp2 = self.client.get('/api/profiles/gallery/')
        self.assertEqual(resp2.status_code, 200)
        data = resp2.data.get('results', resp2.data)
        self.assertIsInstance(data, list)

    def test_committee_create_and_list(self):
        img = _make_image_file('committee.png')
        resp = self.client.post(
            '/api/profiles/committee/',
            {'user': self.user.id, 'pic': img, 'role': 'organizer'},
            format='multipart'
        )
        self.assertEqual(resp.status_code, 201, msg=f"resp.data={resp.data}")
        resp2 = self.client.get('/api/profiles/committee/')
        self.assertEqual(resp2.status_code, 200)
        data = resp2.data.get('results', resp2.data)
        self.assertIsInstance(data, list)
