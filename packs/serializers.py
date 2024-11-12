from rest_framework import serializers
from .models import UserPackInfo, UserPacks, Container,ContainerRequest
from shop.models import Shop
import random
from datetime import datetime


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['name', 'logo', 'x_gis', 'y_gis']


class UserPacksSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = UserPacks
        fields = ['id', 'shop', 'given_date', 'due_date', 'containers', 'user_info']

class UserPackInfoSerializer(serializers.ModelSerializer):
    user_packs = UserPacksSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = UserPackInfo
        fields = ['user_packs', 'user_name', 'user_phone']



class ContainerSerializer(serializers.ModelSerializer):
    code  = serializers.CharField(required=False)
    guarantee_amount = serializers.IntegerField(required=False)
    class Meta:
        model = Container
        fields = ['type', 'code', 'guarantee_amount', 'country', 'date', 'shop']

from rest_framework import serializers
from .models import ContainerRequest, ContainerItemRequest

class ContainerItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerItemRequest
        fields = ['container_type', 'count']

class ContainerRequestSerializer(serializers.ModelSerializer):
    items = ContainerItemRequestSerializer(many=True)

    class Meta:
        model = ContainerRequest
        fields = ['id', 'shop', 'request_date', 'status', 'approval_date', 'denial_reason', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        container_request = ContainerRequest.objects.create(**validated_data)
        for item_data in items_data:
            print(item_data)
            ContainerItemRequest.objects.create(container_request=container_request, **item_data)
        return container_request

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['shop'] = ShopSerializer(Shop.objects.get(pk=representation['shop'])).data
        # Customize the items representation
        items_representation = []
        for item in instance.items.all():
            items_representation.append({
                'container_type': item.container_type,
                'quantity': item.count,
                # You can add more fields here if needed
            })

        # Set the customized items representation back to the representation
        representation['items'] = items_representation

        return representation
class ContainerApprovalSerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    reason = serializers.CharField(required=False)



class NewUserPacksSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    user_info = UserPackInfoSerializer(source='user_pack_id', read_only=True)  # This should correctly reference user_pack_id
    containers = ContainerSerializer(many=True)
    class Meta:
        model = UserPacks
        fields = ['id', 'shop', 'given_date', 'due_date', 'containers', 'user_info']

    def get_containers(self, obj):
        # Fetch related containers where is_loan is False
        return ContainerSerializer(obj.containers.filter(is_loan=False), many=True).data

    def get_loans(self, obj):
        # Fetch related containers where is_loan is False
        return ContainerSerializer(obj.filter(is_loan=True), many=True).data

