from decimal import Decimal
import os

from rest_framework import serializers

from .models import Donation


class DonationCreateSerializer(serializers.Serializer):
    donor_name = serializers.CharField(max_length=120)
    donor_email = serializers.EmailField(required=False, allow_blank=True)
    donor_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    purpose = serializers.CharField(max_length=200, required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))

    def validate_amount(self, value):
        max_amount = Decimal(os.environ.get('DONATION_MAX_AMOUNT', '100000.00'))
        if value > max_amount:
            raise serializers.ValidationError(f'Amount exceeds allowed limit of INR {max_amount}.')
        return value

    def validate_donor_phone(self, value):
        phone = ''.join(ch for ch in (value or '') if ch.isdigit())
        if phone and len(phone) < 10:
            raise serializers.ValidationError('Phone number must have at least 10 digits.')
        return value


class DonationVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(max_length=80)
    razorpay_payment_id = serializers.CharField(max_length=80)
    razorpay_signature = serializers.CharField(max_length=255)


class DonationSerializer(serializers.ModelSerializer):
    receipt_url = serializers.SerializerMethodField()

    def get_receipt_url(self, obj):
        request = self.context.get('request')
        if not request or not obj.receipt_pdf or not obj.receipt_token:
            return None
        return request.build_absolute_uri(f'/api/payments/receipt/{obj.public_id}/?token={obj.receipt_token}')

    class Meta:
        model = Donation
        fields = (
            'public_id',
            'donor_name',
            'donor_email',
            'donor_phone',
            'amount',
            'currency',
            'purpose',
            'status',
            'receipt_number',
            'receipt_url',
            'paid_at',
            'created_at',
        )
