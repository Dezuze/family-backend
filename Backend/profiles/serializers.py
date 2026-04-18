from rest_framework import serializers
from .models import Gallery, Committee, CommunityRole
from families.models import FamilyMember


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('id', 'image', 'date', 'description', 'created_at')


class CommitteeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    pic = serializers.SerializerMethodField()
    member_id = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    church_parish = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    
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

    def get_member_id(self, obj):
        member = getattr(obj.user, 'member', None)
        return getattr(member, 'member_id', None)

    def get_occupation(self, obj):
        member = getattr(obj.user, 'member', None)
        return getattr(member, 'occupation', None)

    def get_education(self, obj):
        member = getattr(obj.user, 'member', None)
        return getattr(member, 'education', None)

    def get_church_parish(self, obj):
        member = getattr(obj.user, 'member', None)
        return getattr(member, 'church_parish', None)

    def get_bio(self, obj):
        member = getattr(obj.user, 'member', None)
        return getattr(member, 'bio', None)

    class Meta:
        model = Committee
        fields = (
            'id', 'name', 'pic', 'role', 'member_id',
            'occupation', 'education', 'church_parish', 'bio', 'created_at'
        )


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
