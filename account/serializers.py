from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, SecretKeyUser , UserAdmin


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email']
    def create(self, validated_data):
        return super().create(validated_data)

class SecretKeyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretKeyUser
        fields = ['id', 'user', 'key']

    def create(self, validated_data):
        # Generate a new TOTP secret key if not provided
        if 'key' not in validated_data or not validated_data['key']:
            validated_data['key'] = pyotp.random_base32()
        return super().create(validated_data)


from rest_framework import serializers
import pyotp


class TOTPVerificationSerializer(serializers.Serializer):
    secret_key = serializers.CharField(write_only=True)
    totp_code = serializers.CharField(write_only=True)

    def validate(self, data):
        secret_key = data.get('secret_key')
        totp_code = data.get('totp_code')
        flag = True
        # Validate the presence of secret key and TOTP code
        if not secret_key or not totp_code:
            raise serializers.ValidationError('Both secret_key and totp_code are required.')

        # Create a TOTP object using the provided secret key
        totp = pyotp.TOTP(secret_key)

        # Verify the TOTP code
        if not totp.verify(totp_code, valid_window=1):
            flag = False
        return flag


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=18)
    code = serializers.CharField(max_length=4)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'is_deleted']

    class UserAdminSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserAdmin
            fields = ['id', 'name', 'email', 'password']
            extra_kwargs = {
                'password': {'write_only': True}  # Password is write-only for security
            }

        # Ensure the password is hashed before saving
        def create(self, validated_data):
            if 'password' in validated_data:
                validated_data['password'] = make_password(validated_data['password'])
            return super().create(validated_data)

        def update(self, instance, validated_data):
            if 'password' in validated_data:
                validated_data['password'] = make_password(validated_data['password'])
            return super().update(instance, validated_data)
