from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly
from .services import ensure_daily_anniversary_posts


def _visibility_q(request):
    if getattr(request.user, 'is_authenticated', False):
        return Q(visibility='public') | Q(visibility='members')
    return Q(visibility='public')


class EventsListView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        ensure_daily_anniversary_posts()
        # Future events: post_type='event' AND event_date >= now
        return Post.objects.filter(
            _visibility_q(self.request),
            post_type='event', 
            event_date__gte=timezone.now()
        ).order_by('event_date')


class NewsListView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        ensure_daily_anniversary_posts()
        # News items OR Past events
        now = timezone.now()
        return Post.objects.filter(
            _visibility_q(self.request),
            Q(post_type='news') |
            Q(post_type='event', event_date__lt=now) |
            Q(post_type='event', event_date__isnull=True) # Fallback if no date set
        ).order_by('-created_at')


class NewsCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # User -> Member
        member = getattr(self.request.user, 'member', None)
        if member:
            post = serializer.save(creator=member, visibility='public', is_auto_generated=False)
            
            # Handle Image Upload
            if 'image' in self.request.FILES:
                from .models import Media
                image = self.request.FILES['image']
                Media.objects.create(
                    uploader=member,
                    post=post,
                    media_url=image,
                    media_type='image'
                )
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"error": "Your user account is not linked to a Family Member profile. Please contact an admin or complete your onboarding to post news."})


class NewsDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        return Post.objects.filter(_visibility_q(self.request))

