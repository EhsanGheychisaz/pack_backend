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
from account.models import TokenModel


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomIsAuthenticated]
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def list(self, request, *args, **kwargs):
        user_id = request.user_id
        try:
            # user_id = TokenModel.objects.get(pk=user_id)
            # user = User.objects.get(id=user_id.model_id)
            return super().list(request, *args, **kwargs)
        except:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the instance to update
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Enable partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='info')
    def info(self, request, *args, **kwargs):
        instance = Shop.objects.filter(pk= request.user_id)
        serializer = ShopSerializer(instance,  many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='last-two')
    def last_two_shops(self, request):
        try:
            # Fetch the last three shops (ordering by the 'id' field)
            last_three_shops = Shop.objects.order_by('-id')[:2]
            serializer = self.get_serializer(last_three_shops, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
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
                return Response({"error": "Shop does not exist or is inactive","problem":"email"}, status=status.HTTP_404_NOT_FOUND)

            if not shop.password or not password == shop.password:
                return Response({"error": "Invalid password or password not set","problem":"password"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(shop)
            return Response({
                'access': str(refresh.access_token),
                'status': "shop"
            }, status=status.HTTP_200_OK)

    def forget_password(self, request):

            email = request.data.get("email")
            print(email)
            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Check if shop or admin exists with this email
                user = Shop.objects.filter(email__exact=email, status='active').get()

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
                    return Response({"error": "No active shop or admin with this email" ,"problem":"email"},
                                    status=status.HTTP_404_NOT_FOUND)

            # Check if reset code matches
            if user.reset_code != reset_code:
                return Response({"error": "Invalid reset code","problem":"reset code"}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.password =  new_password
            user.reset_code = None  # Clear the reset code after successful reset
            user.save()

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)


from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password


class UserManagementView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        if 'change-password' in request.path:
            return self.change_password(request)
        elif 'change-shop-status' in request.path:
            return self.change_shop_status(request)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def change_password(self, request):
        shop_id = request.data.get("shop")
        new_password = request.data.get("new_password")

        if not shop_id or not new_password:
            return Response({"error": "Shop ID and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            shop = Shop.objects.get(id=shop_id, status='active')
        except Shop.DoesNotExist:
            return Response({"error": "Shop not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        # Hash the new password and update the shop
        shop.password = new_password
        shop.save()

        # Send email notification
        send_mail(
            subject="Your Password Has Been Changed",
            message=f"Your password has been successfully changed.  and  it your password {shop.password}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[shop.email],
        )

        return Response({"message": "Password changed successfully and email notification sent."}, status=status.HTTP_200_OK)

    def change_shop_status(self, request):

        shop_id = request.data.get("shop")
        new_status = request.data.get("new_status")

        if not shop_id or not new_status:
            return Response({"error": "Shop ID and new status are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Only allow valid status
        if new_status not in ['active', 'inactive']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the request user is an admin
        # user_email = request.data.get("email")
        # try:
        #     admin = UserAdmin.objects.get(email=user_email)
        # except UserAdmin.DoesNotExist:
        #     return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the shop's status
        try:
            shop = Shop.objects.get(id=shop_id)
            shop.status = new_status
            shop.save()

            # Send email notification
            send_mail(
                subject="Shop Status Changed",
                message=f"The status of your shop has been changed to {new_status}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[shop.email],
            )

            return Response({"message": "Shop status changed successfully and email notification sent."}, status=status.HTTP_200_OK)

        except Shop.DoesNotExist:
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)
