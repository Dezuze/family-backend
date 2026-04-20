from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth import admin as auth_admin
from django.contrib.admin.sites import NotRegistered
from .models import User, InviteToken, ClaimToken
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages

# Unregister any existing registration for the User model (prevents duplicate links)
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin, ModelAdmin):
    list_display = (
        'username',
        'email',
        'member',
        'is_active',
        'is_staff'
    )
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/set-password/', self.admin_site.admin_view(self.user_set_password_view), name='accounts_user_set_password'),
        ]
        return custom_urls + urls

    def user_set_password_view(self, request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            messages.error(request, 'User not found.')
            return redirect('..')

        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Password updated for {user.username}.')
                return redirect('..')
        else:
            form = SetPasswordForm(user)

        context = {
            'title': f'Set password for {user.username}',
            'form': form,
            'opts': self.model._meta,
            'original': user,
        }
        # Use Django admin's built-in change_password template which exists in contrib.admin
        return render(request, 'admin/auth/user/change_password.html', context)

    def change_password_link(self, obj):
        from django.utils.html import format_html
        try:
            # Use Django admin's built-in user password change URL
            url = reverse('admin:auth_user_password_change', args=[obj.pk])
            return format_html('<a class="button" href="{}">Set password</a>', url)
        except Exception:
            return ''

    # Use the admin.display decorator for short_description
    # (Django 3.2+)
    # @admin.display(description='Password')
    # def change_password_link(self, obj): ...
    list_display = list(list_display) + ['change_password_link']
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    ordering = ('username',)

@admin.register(InviteToken)
class InviteTokenAdmin(ModelAdmin):
    list_display = ('token', 'member', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('token', 'created_at')

@admin.register(ClaimToken)
class ClaimTokenAdmin(ModelAdmin):
    list_display = ('token', 'profile', 'username', 'created_by', 'is_claimed', 'created_at')
    list_filter = ('is_claimed', 'created_at')
    readonly_fields = ('token', 'created_at')
    search_fields = ('username', 'profile__name')
