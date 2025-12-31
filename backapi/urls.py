from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', LoginView.as_view()),
path('api/auth/logout/', LogoutView.as_view()),
path('api/auth/me/', MeView.as_view()),

path('api/news/', include('news.urls')),
]
