from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from families.models import Family, FamilyMember
from profiles.models import CommunityRole, Gallery

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


class GalleryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_gallery_create_accepts_video_file(self):
        video_file = SimpleUploadedFile('clip.mp4', b'fake-video-data', content_type='video/mp4')
        res = self.client.post(
            '/api/profiles/gallery/',
            {'image': video_file, 'media_type': 'video', 'description': 'Test clip'},
            format='multipart',
        )
        self.assertEqual(res.status_code, 201)
        gallery = Gallery.objects.latest('id')
        self.assertEqual(gallery.media_type, 'video')
        from pathlib import Path
        self.assertIn(Path(gallery.image.name).suffix.lower(), {'.mp4', '.webm', '.mov'})

    def test_gallery_delete_removes_item(self):
        image_file = SimpleUploadedFile('photo.jpg', b'fake-image-data', content_type='image/jpeg')
        create_res = self.client.post(
            '/api/profiles/gallery/',
            {'image': image_file, 'media_type': 'image', 'description': 'Delete me'},
            format='multipart',
        )
        self.assertEqual(create_res.status_code, 201)
        gallery = Gallery.objects.latest('id')

        delete_res = self.client.delete(f'/api/profiles/gallery/{gallery.id}/')
        self.assertEqual(delete_res.status_code, 204)
        self.assertFalse(Gallery.objects.filter(id=gallery.id).exists())
