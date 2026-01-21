from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.admin.sites import NotRegistered
from .models import User

# Unregister any existing registration for the User model (prevents duplicate links)
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = (
        'username',
        'email',
        'member_id',
        'is_active',
        'is_staff'
    )
    search_fields = ('username', 'email', 'member_id')
    list_filter = ('is_active', 'is_staff')
    ordering = ('username',)
