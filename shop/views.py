from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from .models import Shop
from account.models import User , UserAdmin
from .serializers import ShopSerializer
from account.permissions import CustomIsAuthenticated


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomIsAuthenticated]
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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Shop
from .serializers import ShopSerializer


class ShopAuthView(APIView):

    def post(self, request):
        if 'login' in request.path:
            return self.login(request)
        elif 'register' in request.path:
            return self.register(request)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def register(self, request):
        """
        Handle shop registration without setting the password during registration.
        """
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            # Save the shop without a password
            serializer.save()
            return Response({
                'shop': serializer.data,
                'message': 'Shop registered successfully, password needs to be set manually.',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        email = request.data["email"]
        password = request.data["password"]
        try:
            user = UserAdmin.objects.filter(email=email,password=password).get()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'status':"admin"
            }, status=status.HTTP_200_OK)
        except:
            try:
                shop = Shop.objects.get(email=email, status='active')
            except Shop.DoesNotExist:
                return Response({"error": "Shop does not exist or is inactive"}, status=status.HTTP_404_NOT_FOUND)

            if not shop.password or not password == shop.password:
                return Response({"error": "Invalid password or password not set"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(shop)
            return Response({
                'access': str(refresh.access_token),
                'status': "shop"
            }, status=status.HTTP_200_OK)
