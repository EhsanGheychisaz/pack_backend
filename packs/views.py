from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserPackInfo, UserPacks , Container
from .serializers import UserPackInfoSerializer, UserPacksSerializer , ContainerSerializer
from account.permissions import CustomIsAuthenticated
from account.views import validate
from account.models import User
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action


class UserPackInfoView(APIView):
    permission_classes = [CustomIsAuthenticated]
    def get(self, request, user_id):
        if user_id != request.user_id:
            return  Response(status=403)
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
            'remind': remind,
            "total":remind +user_pack_info.count
        }

        return Response(response_data, status=status.HTTP_200_OK)


from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
import random


class ContainerViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.CreateModelMixin):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer

    def create(self, request, *args, **kwargs):
        # Extracting the data from the request
        country = request.data.get('country')
        container_type = request.data.get('type')
        country_code = Container.CONTAINER_COUNTRY_NUMERICAL_CODE.get(country)
        # Fetch the numerical code for the container type
        numerical_code = Container.CONTAINER_TYPE_NUMERICAL_CODES.get(container_type)

        if not numerical_code:
            return Response({"error": "Invalid container type"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate the code
        current_year = datetime.now().year
        random_start = random.randint(10, 99)
        random_end = random.randint(10, 99)
        generated_code = f'{random_start}{country_code}{numerical_code}{current_year}{random_end}'

        # Add the generated code to the request data
        request.data['code'] = generated_code

        # Use the serializer to save the Container object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return the created container with the generated code
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def types_and_countries(self, request):
        types = Container.CONTAINER_TYPE_CHOICES
        countries = Container.COUNTRY_TYPE_CHOICES
        return Response({
            'types': dict(types),
            'countries': dict(countries)
        })

    @action(detail=False, methods=['post'])
    def generate_codes(self, request):
        country = request.data.get('country')
        container_type = request.data.get('type')
        count = int(request.data.get('count', 1))  # Default to 1 if not provided
        containers = []

        # Retrieve the numerical code based on container type
        numerical_code = Container.CONTAINER_TYPE_NUMERICAL_CODES.get(container_type)
        country_code = Container.CONTAINER_COUNTRY_NUMERICAL_CODE.get(country)
        if not numerical_code:
            return Response({"error": "Invalid container type"}, status=400)

        # Create and save each generated container
        for _ in range(count):
            random_start = random.randint(10, 99)
            random_end = random.randint(10, 99)
            current_year = datetime.now().year
            generated_code = f'{random_start}{country_code}{numerical_code}{current_year}{random_end}'

            # Create a new Container instance
            container = Container.objects.create(
                type=container_type,
                country=country,
                code=generated_code,
                guarantee_amount=request.data.get('guarantee_amount', 0),
                shop_id=request.data.get('shop')  # Make sure the shop is provided in request
            )
            containers.append(container.code)

        return Response({'generated_codes': containers}, status=201)

    @action(detail=False, methods=['post'])
    def add_packs(self, request):
        containers_data = request.data.get('containers')
        user_code = request.data.get('user')

        # Validate the user code (uncomment and implement the validate function)
        # status = validate({'totp_code': user_code})
        # if not status:
        #     return Response({"error": "Invalid user code"}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming user_id is derived from user_code, adapt as necessary
        user_id = 1  # This should be replaced with dynamic retrieval logic
        user = get_object_or_404(User, pk=user_id)

        # Get or create UserPackInfo instance
        user_pack_info, created = UserPackInfo.objects.get_or_create(user=user, defaults={'count': 0})

        containers_to_add = []
        for code in containers_data:
            try:
                # Get the container instance based on the code
                container = get_object_or_404(Container, code=code)
                containers_to_add.append(container)
            except Container.DoesNotExist:
                return Response({"error": f"Container with code {code} does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        # Create UserPacks instance
        user_packs = UserPacks(
            user_pack_id=user_pack_info,
            pack_description="Pack containing specified containers",
            given_date=datetime.now().date(),
            due_date=(datetime.now() + timedelta(weeks=1)).date(),
            shop=containers_to_add[0].shop  # Directly use the shop instance
        )

        # Save the UserPacks instance to generate an ID
        user_packs.save()

        # Assign the containers to the UserPacks instance
        user_packs.containers.set(containers_to_add)  # Use container instances here
        user_packs.containers_num = len(containers_to_add)  # Update container count
        user_packs.save()  # Save the updated UserPacks instance

        # Update the UserPackInfo count
        user_pack_info.count += 1
        user_pack_info.save()  # Save the updated UserPackInfo

        return Response({"message": "User packs added successfully"}, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['put'])
    def update_containers(self, request, pk=None):
        user_pack = self.get_object()
        now = datetime.now()

        if now - user_pack.created_at > timedelta(minutes=2):
            return Response({"error": "You can only update containers within 2 minutes of creation."},
                            status=status.HTTP_400_BAD_REQUEST)

        new_codes = request.data.get('codes', [])
        containers_to_update = []

        for code in new_codes:
            try:
                container = Container.objects.get(code=code)
                containers_to_update.append(container)
            except Container.DoesNotExist:
                return Response({"error": f"Container with code {code} does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        user_pack.containers.set(containers_to_update)
        user_pack.containers_num = len(containers_to_update)
        user_pack.save()

        return Response({"message": "Containers updated successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def loans_by_weekday(self, request):
        today = timezone.now()  # Keep it as datetime
        start_of_week = today - timezone.timedelta(days=today.weekday())

        # Get all UserPacks with related containers
        user_packs = UserPacks.objects.prefetch_related('containers')

        # Create a dictionary to hold counts for each day of the week
        loans_by_day = defaultdict(int)

        for user_pack in user_packs:
            # Ensure that given_date is a datetime object
            loan_date = timezone.make_aware(datetime.combine(user_pack.given_date, datetime.min.time()))

            # Only count if the loan date is within the current week
            if loan_date >= start_of_week:  # Current week
                loans_by_day[loan_date.weekday()] += 1  # 0 = Monday, 6 = Sunday

        # Format the response
        response_data = {
            "loans_by_weekday": {
                "Monday": loans_by_day[0],
                "Tuesday": loans_by_day[1],
                "Wednesday": loans_by_day[2],
                "Thursday": loans_by_day[3],
                "Friday": loans_by_day[4],
                "Saturday": loans_by_day[5],
                "Sunday": loans_by_day[6],
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)