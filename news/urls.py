# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('latest/<str:type>/', LatestNewsView.as_view())
]
