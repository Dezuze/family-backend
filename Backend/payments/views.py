from rest_framework import generics
from .models import DonationOption
from .serializers import DonationOptionSerializer
from rest_framework.permissions import AllowAny

class DonationOptionListView(generics.ListAPIView):
    queryset = DonationOption.objects.filter(is_active=True).order_by('order', 'amount')
    serializer_class = DonationOptionSerializer
    permission_classes = [AllowAny]
