from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = News
        fields = (
            'id',
            'title',
            'description',
            'image',
            'type',
            'created_at'
        )
