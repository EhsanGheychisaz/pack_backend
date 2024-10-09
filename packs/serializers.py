from rest_framework import serializers
from .models import UserPackInfo, UserPacks, Container
from shop.models import Shop
import random
from datetime import datetime


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['name', 'logo', 'x_gis', 'y_gis']


class UserPacksSerializer(serializers.ModelSerializer):
    shop = ShopSerializer( read_only=True)

    class Meta:
        model = UserPacks
        fields = ['shop', 'pack_description', 'given_date', 'due_date','containers']


class UserPackInfoSerializer(serializers.ModelSerializer):
    user_packs = UserPacksSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserPackInfo
        fields = [ 'user_packs', 'user_name']


class ContainerSerializer(serializers.ModelSerializer):
    code  = serializers.CharField(required=False)
    guarantee_amount = serializers.IntegerField(required=False)
    class Meta:
        model = Container
        fields = ['type', 'code', 'guarantee_amount', 'country', 'date', 'shop']