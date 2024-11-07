from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserInfoViewSet ,TOTPVerificationView, LoginView,SendOTPView,UpdateUserView,UserListViewSet , SendTOTPSMS

router = DefaultRouter()
router.register(r'user-info', UserInfoViewSet, basename='user-info')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('send-totp/', SendTOTPSMS.as_view(), name='send-totp'),
    path('verify-totp/', TOTPVerificationView.as_view(), name='verify_totp'),
    path('user/', UpdateUserView.as_view(), name='update-user'),
    path('users-list/',UserListViewSet.as_view() , name='list-user'),

]