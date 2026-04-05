from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Gallery, Committee
from .serializers import GallerySerializer, CommitteeSerializer


class GalleryListCreateView(ListCreateAPIView):
	queryset = Gallery.objects.all().order_by('-created_at')
	serializer_class = GallerySerializer
	permission_classes = [AllowAny]


class CommitteeListCreateView(ListCreateAPIView):
	queryset = Committee.objects.all().order_by('-created_at')
	serializer_class = CommitteeSerializer

	def get_permissions(self):
		if self.request.method == 'GET':
			return [AllowAny()]
		return [IsAuthenticated()]
