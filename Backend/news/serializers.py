from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)

    class Meta:
        model = News
        fields = (
            'id',
            'title',
            'description',
            'image',
            'type',
            'event_date',
            'location',
            'created_at',
            'author_name',
            'author_id'
        )
