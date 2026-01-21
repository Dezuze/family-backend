import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from accounts.models import User

username = 'wesly'
password = 'wesly'
email = 'wesly@example.com'
member_id = 'wesly'

u = User.objects.filter(username=username).first()
if u is None:
    u = User(username=username, email=email, member_id=member_id)
    u.set_password(password)
    u.save()
    print('created', u.id)
else:
    u.set_password(password)
    u.save()
    print('updated', u.id)
