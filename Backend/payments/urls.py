from django.urls import path
from .views import DonationOptionListView

urlpatterns = [
    path('options/', DonationOptionListView.as_view(), name='donation-options'),
]
