from django.urls import path

from .views import (
    DonationMyHistoryView,
    DonationOrderCreateView,
    DonationReceiptDownloadView,
    DonationVerifyView,
    RazorpayWebhookView,
)

urlpatterns = [
    path('create-order/', DonationOrderCreateView.as_view()),
    path('verify/', DonationVerifyView.as_view()),
    path('webhook/', RazorpayWebhookView.as_view()),
    path('my-donations/', DonationMyHistoryView.as_view()),
    path('receipt/<uuid:public_id>/', DonationReceiptDownloadView.as_view()),
]
