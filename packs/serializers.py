from rest_framework import serializers
from .models import UserPackInfo, UserPacks
from shop.models import Shop


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['name', 'logo', 'x_gis', 'y_gis']
class UserPacksSerializer(serializers.ModelSerializer):
    shop = ShopSerializer( read_only=True)
    class Meta:
        model = UserPacks
        fields = ['shop', 'pack_description', 'given_date', 'due_date']

class UserPackInfoSerializer(serializers.ModelSerializer):
    user_packs = UserPacksSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserPackInfo
        fields = [ 'user_packs', 'user_name']
