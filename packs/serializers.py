from rest_framework import serializers
from .models import UserPackInfo, UserPacks

class UserPacksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPacks
        fields = ['pack_title', 'pack_description', 'given_date', 'due_date']

class UserPackInfoSerializer(serializers.ModelSerializer):
    user_packs = UserPacksSerializer(many=True, read_only=True)

    class Meta:
        model = UserPackInfo
        fields = ['count', 'user_packs']
