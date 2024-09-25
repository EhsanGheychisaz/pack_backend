from rest_framework import serializers
from .models import UserPackInfo, UserPacks
from shop.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'logo', 'x_gis', 'y_gis']
class UserPacksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPacks
        fields = ['pack_title', 'pack_description', 'given_date', 'due_date']

class UserPackInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(many=True, read_only=True)
    user_packs = UserPacksSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserPackInfo
        fields = ['shop', 'user_packs', 'user_name']
