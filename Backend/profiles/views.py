from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from .models import Gallery, Committee
from .serializers import GallerySerializer, CommitteeSerializer


class GalleryListCreateView(ListCreateAPIView):
	queryset = Gallery.objects.all().order_by('-created_at')
	serializer_class = GallerySerializer
	permission_classes = [AllowAny]


class CommitteeListCreateView(ListCreateAPIView):
	queryset = Committee.objects.all().order_by('-created_at')
	serializer_class = CommitteeSerializer
	permission_classes = [AllowAny]
