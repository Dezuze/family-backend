from rest_framework import serializers
from .models import FamilyMember

class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = '__all__'

class FamilyTreeSerializer(serializers.ModelSerializer):
    # Simplified structure for D3
    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'photo', 'relation', 'parents', 'spouse', 'children']
        depth = 1 # Simple depth to see Names of related objects
