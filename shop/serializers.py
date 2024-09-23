from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'email', 'phone', 'password', 'status', 'logo', 'x_gis', 'y_gis']

    # Ensure the password is hashed before saving
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
