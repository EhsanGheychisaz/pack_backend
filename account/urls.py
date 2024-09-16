from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserInfoViewSet ,TOTPVerificationView, LoginView,SendOTPView,UpdateUserView

router = DefaultRouter()
router.register(r'user-info', UserInfoViewSet, basename='user-info')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-totp/', TOTPVerificationView.as_view(), name='verify_totp'),
    path('user/', UpdateUserView.as_view(), name='update-user'),
]