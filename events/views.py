from rest_framework.viewsets import ModelViewSet
from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import IsAuthenticated

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
