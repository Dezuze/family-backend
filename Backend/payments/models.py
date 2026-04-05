import secrets
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class Donation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    donor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations',
    )
    donor_member = models.ForeignKey(
        'families.FamilyMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations',
    )

    donor_name = models.CharField(max_length=120)
    donor_email = models.EmailField(blank=True, null=True)
    donor_phone = models.CharField(max_length=20, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    purpose = models.CharField(max_length=200, blank=True, null=True)

    razorpay_order_id = models.CharField(max_length=80, unique=True)
    razorpay_payment_id = models.CharField(max_length=80, blank=True, null=True, unique=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    receipt_number = models.CharField(max_length=40, blank=True, null=True, unique=True)
    receipt_pdf = models.FileField(upload_to='receipts/', blank=True, null=True)
    receipt_token = models.CharField(max_length=120, blank=True, null=True, unique=True)

    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Donation {self.razorpay_order_id} ({self.status})"

    @property
    def amount_paise(self):
        return int((self.amount or Decimal('0')) * 100)

    def ensure_receipt_token(self):
        if not self.receipt_token:
            self.receipt_token = secrets.token_urlsafe(36)
