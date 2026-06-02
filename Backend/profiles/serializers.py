from rest_framework import serializers
from .models import Gallery, CommunityRole
from families.models import FamilyMember


class GallerySerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ('id', 'image', 'media_url', 'media_type', 'date', 'description', 'created_at')

    def get_media_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CommunityRoleSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=FamilyMember.objects.all(),
        required=False,
    )

    class Meta:
        model = CommunityRole
        fields = ('id', 'name', 'priority', 'can_manage_all', 'is_active', 'members', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        normalized = ' '.join(str(value or '').strip().split())
        if not normalized:
            raise serializers.ValidationError('Role name is required.')

        qs = CommunityRole.objects.filter(name__iexact=normalized)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Role already exists.')
        return normalized
