from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Shop

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'email', 'phone', 'password', 'status', 'logo', 'x_gis', 'y_gis']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'logo': {'required': False},
            'name': {'required': False},
            'phone': {'required': False},
            'x_gis': {'required': False},
            'y_gis': {'required': False}
        }

    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
