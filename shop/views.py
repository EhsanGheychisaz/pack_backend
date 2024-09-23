from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from .models import Shop
from .serializers import ShopSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            shop = Shop.objects.get(email=email)
        except Shop.DoesNotExist:
            return Response({'detail': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)

        if shop.status != 'active':
            return Response({'detail': 'Shop is not active'}, status=status.HTTP_403_FORBIDDEN)

        if not check_password(password, shop.password):
            return Response({'detail': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'id': shop.id,
            'name': shop.name,
            'email': shop.email,
            'phone': shop.phone,
            'logo': shop.logo.url if shop.logo else None,
        }, status=status.HTTP_200_OK)


