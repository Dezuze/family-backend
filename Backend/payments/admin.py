from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'razorpay_order_id',
        'donor_name',
        'amount',
        'status',
        'receipt_number',
        'created_at',
    )
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'donor_name', 'donor_email', 'receipt_number')
    list_filter = ('status', 'created_at')
    readonly_fields = ('public_id', 'created_at', 'updated_at')
