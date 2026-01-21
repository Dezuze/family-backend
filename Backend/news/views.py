from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import News
from .serializers import NewsSerializer
from .permissions import IsAuthorOrReadOnly


class EventsListView(ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        # Future events: type='event' AND event_date >= now
        return News.objects.filter(
            type='event', 
            event_date__gte=timezone.now()
        ).order_by('event_date')


class NewsListView(ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        # News items OR Past events
        now = timezone.now()
        return News.objects.filter(
            Q(type='news') | 
            Q(type='event', event_date__lt=now) |
            Q(type='event', event_date__isnull=True) # Fallback if no date set
        ).order_by('-created_at')


class NewsCreateView(ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NewsDetailView(RetrieveDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthorOrReadOnly]

