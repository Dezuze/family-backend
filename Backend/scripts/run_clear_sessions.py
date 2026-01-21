import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from django.contrib.sessions.models import Session

Session.objects.all().delete()
print('All sessions deleted')
