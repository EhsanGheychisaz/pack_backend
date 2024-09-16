from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserPackInfo, UserPacks
from .serializers import UserPackInfoSerializer, UserPacksSerializer


# Create your views here.
class UserPackInfoView(APIView):
    def get(self, request, user_id):
        # Fetch the UserPackInfo for the user
        user_pack_info = get_object_or_404(UserPackInfo, user_id=user_id)

        # Fetch the associated UserPacks
        user_packs = UserPacks.objects.filter(user_pack_id=user_pack_info)

        # Calculate the remind value
        count = user_pack_info.count
        remind = 5 - count

        # Serialize the data
        user_pack_info_serializer = UserPackInfoSerializer(user_pack_info)
        user_packs_serializer = UserPacksSerializer(user_packs, many=True)

        # Prepare the response data
        response_data = {
            'user_pack_info': user_pack_info_serializer.data,
            'user_packs': user_packs_serializer.data,
            'remind': remind
        }

        return Response(response_data, status=status.HTTP_200_OK)
