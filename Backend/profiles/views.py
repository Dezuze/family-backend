from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Gallery, Committee, CommunityRole
from .serializers import GallerySerializer, CommitteeSerializer, CommunityRoleSerializer


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


class CommunityRoleListCreateView(ListCreateAPIView):
	serializer_class = CommunityRoleSerializer

	def get_queryset(self):
		base_qs = CommunityRole.objects.order_by('priority', 'name')
		if self.request.method == 'GET':
			return base_qs.filter(is_active=True)
		return base_qs

	def get_permissions(self):
		if self.request.method == 'GET':
			return [AllowAny()]
		return [IsAuthenticated()]
