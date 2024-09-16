from django.urls import path
from .views import UserPackInfoView

urlpatterns = [
    path('<int:user_id>/baseuser/', UserPackInfoView.as_view(), name='user-pack-info'),
]
