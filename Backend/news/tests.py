from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from .models import News


def _make_image_file(name: str = 'news.png') -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new('RGB', (2, 2), color='blue').save(buffer, format='PNG')
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type='image/png')


class NewsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        for i in range(3):
            News.objects.create(title=f'News {i}', description='desc', image=_make_image_file(f'news_{i}.png'), type='news')
        for i in range(2):
            News.objects.create(title=f'Event {i}', description='desc', image=_make_image_file(f'event_{i}.png'), type='event')

    def test_latest_news_endpoint(self):
        resp = self.client.get('/api/news/latest/news/')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.get('results', resp.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        for item in data:
            self.assertEqual(item.get('type'), 'news')

    def test_latest_event_endpoint(self):
        resp = self.client.get('/api/news/latest/event/')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.get('results', resp.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item.get('type'), 'event')

    def test_latest_unknown_type_returns_empty(self):
        resp = self.client.get('/api/news/latest/unknown/')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.get('results', resp.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_latest_limits_to_10(self):
        for i in range(10):
            News.objects.create(title=f'Extra {i}', description='desc', image=_make_image_file(f'extra_{i}.png'), type='news')
        resp = self.client.get('/api/news/latest/news/')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.get('results', resp.data)
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 10)

