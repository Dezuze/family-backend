from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.shortcuts import redirect
from accounts.views import CsrfInitView
from backapi.views import health_check

urlpatterns = [
    # Redirect the site root to the admin dashboard
    path('', lambda request: redirect('admin:index')),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    # families API mounted at /api/families/
    path('api/families/', include('families.urls')),
    # accounts auth endpoints mounted at /api/auth/
    path('api/auth/', include('accounts.urls')),
    # news endpoints
    path('api/news/', include('news.urls')),
    # profiles endpoints (committee, gallery, community roles)
    path('api/profiles/', include('profiles.urls')),
    # CSRF init endpoint expected by frontend
    path('api/csrf/', CsrfInitView.as_view()),
    # payments endpoints
    path('api/payments/', include('payments.urls')),
    # Serve uploaded media files in both development and production Docker setup
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
