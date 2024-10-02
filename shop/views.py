from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from .models import Shop
from account.models import User , UserAdmin
from .serializers import ShopSerializer
from account.permissions import CustomIsAuthenticated
import random
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings


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
        elif 'forget-password' in request.path:
            return self.forget_password(request)
        elif 'reset-password' in request.path:
            return self.reset_password(request)
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
        print(UserAdmin.objects.filter(email=email).get().password)
        try:
            user = UserAdmin.objects.filter(email=email,password=password).get()
            print(user)
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

    def forget_password(self, request):

            email = request.data.get("email")
            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Check if shop or admin exists with this email
                user = Shop.objects.get(email=email, status='active')
            except Shop.DoesNotExist:
                try:
                    user = UserAdmin.objects.get(email=email)
                except UserAdmin.DoesNotExist:
                    return Response({"error": "No active shop or admin with this email"},
                                    status=status.HTTP_404_NOT_FOUND)

            # Generate a random code and save it to the user (temporary storage)
            reset_code = get_random_string(6, allowed_chars='0123456789')  # 6-digit reset code
            user.reset_code = reset_code
            user.save()

            # Send email
            send_mail(
                subject="Password Reset Code",
                message=f"Your password reset code is: {reset_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)

    def reset_password(self, request):

            email = request.data.get("email")
            reset_code = request.data.get("reset_code")
            new_password = request.data.get("new_password")

            if not email or not reset_code or not new_password:
                return Response({"error": "Email, reset code, and new password are required"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                # Check if shop or admin exists with this email
                user = Shop.objects.get(email=email, status='active')
            except Shop.DoesNotExist:
                try:
                    user = UserAdmin.objects.get(email=email)
                except UserAdmin.DoesNotExist:
                    return Response({"error": "No active shop or admin with this email"},
                                    status=status.HTTP_404_NOT_FOUND)

            # Check if reset code matches
            if user.reset_code != reset_code:
                return Response({"error": "Invalid reset code"}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.password =  new_password
            user.reset_code = None  # Clear the reset code after successful reset
            user.save()

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
