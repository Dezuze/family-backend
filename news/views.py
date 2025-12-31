from rest_framework.generics import ListAPIView
from .models import News
from .serializers import NewsSerializer

class LatestNewsView(ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        news_type = self.kwargs['type']
        return News.objects.filter(type=news_type)[:10]
