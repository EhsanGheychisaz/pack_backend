from django.urls import path,include
from .views import UserPackInfoView
from rest_framework.routers import DefaultRouter
from .views import ContainerViewSet,ContainerRequestViewSet  # Adjust the import based on your project structure

router = DefaultRouter()

router.register(r'containers', ContainerViewSet, basename='container')
router.register(r'container-requests', ContainerRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:user_id>/baseuser/', UserPackInfoView.as_view(), name='user-pack-info'),
]
