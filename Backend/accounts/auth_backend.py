from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) |
                Q(email=username) |
                Q(member_id=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
