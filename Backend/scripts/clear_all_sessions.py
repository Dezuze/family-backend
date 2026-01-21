from django.contrib.sessions.models import Session

Session.objects.all().delete()
print('All sessions deleted')
