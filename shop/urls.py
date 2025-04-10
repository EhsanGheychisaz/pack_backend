from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet ,ShopAuthView,UserManagementView

router = DefaultRouter()
router.register(r'shop', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', ShopAuthView.as_view(), name='shop-login'),
    path('register/', ShopAuthView.as_view(), name='shop-login'),
    path('forget-password/', ShopAuthView.as_view(), name='shop-login'),
    path('reset-password/', ShopAuthView.as_view(), name='shop-login'),
    path('change-password/', UserManagementView.as_view(), name='change-password'),
    path('change-shop-status/', UserManagementView.as_view(), name='change-shop-status'),
]
