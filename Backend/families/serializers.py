from rest_framework import serializers
from .models import FamilyMember, Relationship, FamilyCommitteeMember

class RelationshipSerializer(serializers.ModelSerializer):
    to_member_name = serializers.CharField(source='to_member.name', read_only=True)
    
    class Meta:
        model = Relationship
        fields = ['id', 'to_member', 'to_member_name', 'relation_type', 'is_inferred']

class FamilyMemberSerializer(serializers.ModelSerializer):
    relation = serializers.SerializerMethodField()
    role = serializers.ReadOnlyField()
    is_committee = serializers.ReadOnlyField()
    profile_pic = serializers.SerializerMethodField()
    has_account = serializers.SerializerMethodField()
    relationships = RelationshipSerializer(source='relationships_from', many=True, read_only=True)
    # Frontend expects `committee_role` and an `address` / `location` key.
    committee_role = serializers.CharField(read_only=True)
    address = serializers.CharField(source='address_if_different', read_only=True, allow_null=True)
    location = serializers.CharField(source='address_if_different', read_only=True, allow_null=True)

    class Meta:
        model = FamilyMember
        fields = [
            'id', 'member_id', 'name', 'name_ml', 'nickname', 'age', 'gender', 'relation', 'role', 'is_committee',
            'date_of_birth', 'date_of_death', 'wedding_anniversary', 'blood_group', 'is_deceased', 'is_independent', 'has_account',
            'phone_no', 'email_id', 'photo',
            'profile_pic', 'bio', 'occupation', 'education', 'address_if_different', 
            'address', 'location', 'committee_role', 'place_of_work', 'church_parish', 'parents', 'created_by', 'relationships', 'generation'
        ]
        extra_kwargs = {
            'parents': {'required': False},
            'created_by': {'read_only': True},
            'date_of_birth': {'required': False, 'allow_null': True},
            'date_of_death': {'required': False, 'allow_null': True},
            'member_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'generation': {'required': False, 'allow_null': True},
        }

    def get_profile_pic(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_has_account(self, obj):
        return hasattr(obj, 'user_account') and obj.user_account is not None

    def get_relation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            viewer_member = getattr(request.user, 'member', None)
            if viewer_member:
                rel = Relationship.objects.filter(
                    from_member_id=viewer_member.id,
                    to_member_id=obj.id,
                ).values_list('relation_type', flat=True).first()
                if rel:
                    return rel
        return obj.relation

class FamilyTreeSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()
    is_committee = serializers.ReadOnlyField()

    class Meta:
        model = FamilyMember
        fields = ['id', 'member_id', 'name', 'name_ml', 'role', 'is_committee', 'photo', 'parents', 'children', 'generation']
        depth = 1 



class FamilyCommitteeMemberSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='member_code', required=False, allow_null=True, allow_blank=True)
    photo_url = serializers.SerializerMethodField()
    phone_no = serializers.SerializerMethodField()
    email_id = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    church_parish = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    class Meta:
        model = FamilyCommitteeMember
        fields = [
            'id', 'term_label', 'category', 'role_title', 'name', 'house_name',
            'member', 'member_id', 'phone_no', 'email_id', 'photo', 'photo_url',
            'occupation', 'education', 'church_parish', 'bio',
            'display_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        if obj.member and obj.member.photo:
            return obj.member.photo.url
        return None

    def get_phone_no(self, obj):
        if obj.phone_no:
            return obj.phone_no
        if obj.member and obj.member.phone_no:
            return obj.member.phone_no
        return None

    def get_email_id(self, obj):
        if obj.email_id:
            return obj.email_id
        if obj.member and obj.member.email_id:
            return obj.member.email_id
        return None

    def get_occupation(self, obj):
        if obj.member and obj.member.occupation:
            return obj.member.occupation
        return None

    def get_education(self, obj):
        if obj.member and obj.member.education:
            return obj.member.education
        return None

    def get_church_parish(self, obj):
        if obj.member and obj.member.church_parish:
            return obj.member.church_parish
        return None

    def get_bio(self, obj):
        if obj.member and obj.member.bio:
            return obj.member.bio
        if obj.house_name:
            return obj.house_name
        return None
