from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Gallery, Committee, CommunityRole
from .serializers import GallerySerializer, CommitteeSerializer, CommunityRoleSerializer
from rest_framework.views import APIView


class CommunityRoleManageFlagView(APIView):
	"""Admin-only endpoint to set `can_manage_all` and optionally update members on a CommunityRole.

	POST body:
	  {
		"can_manage_all": true|false,
		"members": [1,2,3]  # optional list of FamilyMember ids to set
	  }
	"""
	permission_classes = [IsAuthenticated, IsAdminUser]

	def post(self, request, pk):
		try:
			role = CommunityRole.objects.get(pk=pk)
		except CommunityRole.DoesNotExist:
			return Response({"error": "Not found"}, status=404)

		data = request.data
		if 'can_manage_all' in data:
			role.can_manage_all = bool(data.get('can_manage_all'))

		if 'members' in data:
			try:
				member_ids = list(map(int, data.get('members') or []))
				role.members.set(member_ids)
			except Exception:
				return Response({"error": "Invalid members list"}, status=400)

		role.save()
		return Response(CommunityRoleSerializer(role).data)


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
		# Allow any to view roles, and authenticated users may create them.
		if self.request.method == 'GET':
			return [AllowAny()]
		# Tests and UI expect any authenticated user to be able to create roles
		return [IsAuthenticated()]


class CommunityRoleDetailView(RetrieveUpdateDestroyAPIView):
	queryset = CommunityRole.objects.all()
	serializer_class = CommunityRoleSerializer

	def get_permissions(self):
		# Allow read to anyone; mutations require admin
		if self.request.method == 'GET':
			return [AllowAny()]
		return [IsAuthenticated(), IsAdminUser()]
