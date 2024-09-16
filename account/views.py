from django.shortcuts import render
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User
from .permissions import CustomIsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer



from rest_framework import viewsets, status
from rest_framework.response import Response
import pyotp
from .models import User, SecretKeyUser
from .serializers import UserSerializer, SecretKeyUserSerializer

class UserInfoViewSet(viewsets.ViewSet):
    permission_classes = [CustomIsAuthenticated]

    def list(self, request):
        user_id = request.user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if a secret key exists for the user
        try:
            secret_key_user = SecretKeyUser.objects.get(user=user)
        except SecretKeyUser.DoesNotExist:
            # Generate a new secret key if none exists
            secret_key = pyotp.random_base32()
            secret_key_user = SecretKeyUser(user=user, key=secret_key)
            secret_key_user.save()

        user_info = {
            "id": user.id,
            "username": user.name,
            "secret_key": secret_key_user.key  # Include the secret key in the response
        }
        return Response(user_info, status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TOTPVerificationSerializer


from django.shortcuts import get_object_or_404
import pyotp
from .models import User

from django.shortcuts import get_object_or_404
import pyotp
from .models import User, SecretKeyUser

def validate(data):
    totp_code = data.get('totp_code')

    # Ensure totp_code is long enough to contain code and user_id
    if len(totp_code) <= 4:
        return False

    # Extract the 4-digit TOTP code and the remaining user_id
    code = totp_code[:4]  # First 4 characters are the TOTP code
    user_id = totp_code[4:]  # Remaining characters are the user ID

    # Fetch the user using the user_id
    user = get_object_or_404(User, id=user_id)

    # Fetch the secret key from the SecretKeyUser model
    secret_key_user = get_object_or_404(SecretKeyUser, user=user)
    secret_key = secret_key_user.key  # Extract the secret key

    # Generate the TOTP object with the retrieved secret_key and 120-second interval
    totp = pyotp.TOTP(secret_key, interval=120)

    # Verify the TOTP code with a valid window of 1
    if totp.verify(code, valid_window=1):
        return True
    return False





class TOTPVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        flag = validate(data=request.data)
        print(flag)
        if flag:
            return Response({'message': 'TOTP code is valid'}, status=status.HTTP_200_OK)
        return Response({'message': 'TOTP code is not valid'}, status=status.HTTP_403_FORBIDDEN)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, SMSComfirmCode
from .serializers import LoginSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']

            try:
                # Check if the user exists
                user = User.objects.get(phone=phone, is_deleted=False)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            # Verify the OTP code
            try:
                confirm_code = SMSComfirmCode.objects.filter(user=user).latest('generated_at')
                if confirm_code.code != code:
                    return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the code has expired (e.g., 10 minutes)
                time_diff = timezone.now() - confirm_code.generated_at
                if time_diff.total_seconds() > 600:
                    return Response({"error": "Confirmation code expired"}, status=status.HTTP_400_BAD_REQUEST)

            except SMSComfirmCode.DoesNotExist:
                return Response({"error": "Confirmation code not found"}, status=status.HTTP_404_NOT_FOUND)

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .sms import generateConfirmCode

class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user by phone or create a new user
        try:
            user = User.objects.get(phone=phone, is_deleted=False)
        except User.DoesNotExist:
            user = User.objects.create(phone=phone, name=f"User {phone}", email=f"{phone}@example.com")

        # Generate and send the confirmation code
        if generateConfirmCode(user):
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UpdateUserSerializer

class UpdateUserView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def put(self, request):
        user_id = request.user_id
        try:
            # Fetch the user by their ID
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Pass the request data to the serializer, excluding the phone field
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Save the updated fields
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
