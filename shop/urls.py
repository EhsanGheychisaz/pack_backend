from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet , ShopLoginView

router = DefaultRouter()
router.register(r'shop', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', ShopLoginView.as_view(), name='shop-login'),
]
