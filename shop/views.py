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
    #
    # @action(detail=False, methods=['post'], url_path='login')
    # def login(self, request):
    #     email = request.data.get('email')
    #     password = request.data.get('password')
    #
    #     try:
    #         shop = Shop.objects.get(email=email)
    #     except Shop.DoesNotExist:
    #         return Response({'detail': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     if shop.status != 'active':
    #         return Response({'detail': 'Shop is not active'}, status=status.HTTP_403_FORBIDDEN)
    #
    #     if not check_password(password, shop.password):
    #         return Response({'detail': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    #
    #     return Response({
    #         'id': shop.id,
    #         'name': shop.name,
    #         'email': shop.email,
    #         'phone': shop.phone,
    #         'logo': shop.logo.url if shop.logo else None,
    #     }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ShopSerializer
from .models import Shop

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Shop
from .serializers import ShopSerializer
from rest_framework.permissions import IsAuthenticated

class ShopLoginView(APIView):
    # permission_classes = [IsAuthenticated]  # Require authentication for the list view

    def post(self, request):
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            password = request.data["password"]

            try:
                # Check if the shop exists and is active
                shop = Shop.objects.get(email=email, status='active')
            except Shop.DoesNotExist:
                return Response({"error": "Shop does not exist or is inactive"}, status=status.HTTP_404_NOT_FOUND)

            if not check_password(password, shop.password):
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(shop)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        shops = Shop.objects.filter(status='active')  # Retrieve only active shops
        serializer = ShopSerializer(shops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
