from rest_framework import serializers
from .models import Gallery, Committee


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('id', 'image', 'date', 'description', 'created_at')


class CommitteeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    # Ideally link to FamilyMember name if possible, but username is okay for now.
    
    class Meta:
        model = Committee
        fields = ('id', 'user', 'name', 'pic', 'role', 'created_at')
