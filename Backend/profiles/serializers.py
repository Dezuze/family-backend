from rest_framework import serializers
from .models import Gallery, Committee


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('id', 'image', 'date', 'description', 'created_at')


class CommitteeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    pic = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        # Try to find family member linked to this user
        if hasattr(obj.user, 'member') and obj.user.member:
            return obj.user.member.name
        return obj.user.get_full_name() or obj.user.username

    def get_role(self, obj):
        if hasattr(obj.user, 'member') and obj.user.member:
            if obj.user.member.committee_role:
                return obj.user.member.committee_role
        return obj.role or 'Committee Member'

    def get_pic(self, obj):
        if obj.pic:
            return obj.pic.url
        if hasattr(obj.user, 'member') and obj.user.member and obj.user.member.photo:
            return obj.user.member.photo.url
        return None

    class Meta:
        model = Committee
        fields = ('id', 'name', 'pic', 'role', 'created_at')
