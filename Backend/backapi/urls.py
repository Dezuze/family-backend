from django.contrib import admin
from django.urls import path, include
from accounts.views import CsrfInitView
from backapi.views import health_check

urlpatterns = [
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
]
