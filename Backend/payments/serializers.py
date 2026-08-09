from rest_framework import serializers
from .models import DonationOption

class DonationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationOption
        fields = ['id', 'title', 'amount', 'purpose', 'upi_id', 'payee_name', 'order']
