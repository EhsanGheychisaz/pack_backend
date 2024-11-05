from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Count
from .models import UserPackInfo, UserPacks , Container
from .serializers import UserPackInfoSerializer, UserPacksSerializer , ContainerSerializer, ContainerRequestSerializer,ContainerApprovalSerializer , NewUserPacksSerializer
from account.permissions import CustomIsAuthenticated
from account.models import User
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone


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
    permission_classes = [CustomIsAuthenticated]

    @action(detail=False, methods=['post'])
    def request_container(self, request):
        shop_id = request.user_id


        container_requests = request.data.get('containers', [])
        if not container_requests:
            return Response({'error': 'No container requests provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Construct the main ContainerRequest object
        request_data = {
            'shop': shop_id,  # Use the valid ID from the retrieved User object
            'items': container_requests
        }

        serializer = ContainerRequestSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Requests for containers successfully created'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve_or_deny(self, request, pk=None):
        # Fetch the ContainerRequest object
        container_request = get_object_or_404(ContainerRequest, pk=pk)
        serializer = ContainerApprovalSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        approved = serializer.validated_data.get('approved')
        reason = serializer.validated_data.get('reason', '')

        if approved:
            # Retrieve available containers matching the request type and count
            available_containers = Container.objects.filter(
                type=container_request.container_type,
                shop__isnull=True
            )[:container_request.count]

            if available_containers.count() < container_request.count:
                return Response(
                    {
                        'error': f'Not enough available containers for type {container_request.container_type}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Assign the available containers to the requesting shop
            for container in available_containers:
                container.shop = container_request.shop
                container.save()

            container_request.status = 'APPROVED'
            container_request.approval_date = timezone.now()
            container_request.save()

            return Response(
                {'status': 'Container request approved and containers assigned'},
                status=status.HTTP_200_OK
            )
        else:
            # Deny the request and save the reason
            container_request.status = 'DENIED'
            container_request.denial_reason = reason
            container_request.save()

            return Response(
                {'status': 'Container request denied', 'reason': reason},
                status=status.HTTP_200_OK
            )
    @action(detail=False, methods=['post'])
    def return_container(self, request):
        container_codes = request.data.get("containers", [])
        shop_id = request.user_id
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return Response(
                {"error": "Shop not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        print(container_codes)
        for code in container_codes:
            container = Container.objects.filter(code=code).first()

            if container:
                # Find all UserPacks that contain this container
                user_packs = UserPacks.objects.filter(containers=container)

                for user_pack in user_packs:
                    # Remove the container from each user pack
                    user_pack.containers.remove(container)

        return Response(
            {"message": "Containers returned to shop successfully"},
            status=status.HTTP_200_OK
        )
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
        user_id = request.data.get('user')
        user = get_object_or_404(User, pk=user_id)
        user_pack_info_exists = UserPackInfo.objects.filter(user_id=user.id).exists()
        if not user_pack_info_exists:
            # Initialize the serializer with the correct user reference
            UserPackInfo.objects.create(user_id=user_id, count=0)

        # Retrieve the UserPackInfo instance
        user_pack_info = UserPackInfo.objects.get(user_id=user.id)

        # Process the containers
        containers_to_add = []
        for code in containers_data:
            try:
                # Get the container instance based on the code
                container = Container.objects.filter(code=code, is_loan=False).get()
                container.is_loan = True
                container.save()
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
        user_packs.save()

        # Set containers and update container count
        user_packs.containers.set(containers_to_add)
        user_packs.containers_num = len(containers_to_add)
        user_packs.save()

        # Update the count in UserPackInfo
        user_pack_info.count += 1
        user_pack_info.save()

        return Response(
            {
                "message": "User packs added successfully",
                "user_pack_id": NewUserPacksSerializer(UserPacks.objects.filter(pk=user_packs.id), many=True).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'])
    def update_containers(self, request, pk=None):
        print(pk)
        user_pack = UserPacks.objects.filter(pk=pk).get()
        print(user_pack)
        now = datetime.now()
        if user_pack.given_date.tzinfo is None:
            given_date = timezone.make_aware(user_pack.given_date, timezone.get_current_timezone())

            if given_date > timedelta(minutes=2):
                return Response({"error": "You can only update containers within 2 minutes of creation."},
                                status=status.HTTP_400_BAD_REQUEST)

        new_codes = request.data.get('containers', [])
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
        data = UserPacksSerializer(UserPacks.objects.filter(pk=user_pack.id) , many=True).data

        return Response({"message": "Containers updated successfully"  ,  "user_pack": data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def loans_by_weekday(self, request):
        today = timezone.now()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        _id = request.user_id
        # Get all UserPacks with related containers
        user_packs = UserPacks.objects.prefetch_related('containers').filter(containers__shop_id=_id)
        shop_pack = Container.objects.filter(shop_id=_id)
        # Create a dictionary to hold counts for each day of the week
        loans_by_day = defaultdict(int)
        users = UserPacks.objects.prefetch_related('containers')\
    .filter(containers__shop_id=_id)\
    .aggregate(unique_count=Count('user_pack_id', distinct=True))['unique_count']
        numerical_code = Container.CONTAINER_TYPE_NUMERICAL_CODES
        for user_pack in user_packs:
            # Ensure that given_date is a datetime object
            loan_date = timezone.make_aware(datetime.combine(user_pack.given_date, datetime.min.time()))
            print(loan_date, start_of_week)
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
            },
            'loans_pack' : user_packs.count(),
            'shop_pack' : shop_pack.count(),
            'users' : users,
            'type': len(numerical_code)

        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def info_admin(self, request):
        today = timezone.now()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        _id = request.user_id
        # Get all UserPacks with related containers
        user_packs = UserPacks.objects.prefetch_related('containers').filter(containers__shop__isnull=False).all()
        shop_pack = Container.objects.filter(shop__isnull=False).all()
        # Create a dictionary to hold counts for each day of the week
        # Format the response
        response_data = {
            'loans_pack': user_packs.count(),
            'container_pack': shop_pack.count(),
            'shops': Shop.objects.filter(status='active').count(),

        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def loans_and_packs_by_container_type(self, request):
        shop_id = request.user_id  # Assuming this represents the shop ID
        all_container_types = Container.objects.values_list('type', flat=True).distinct()
        print(all_container_types)
        # Count loans (UserPacks) by container type for the specific shop
        loans_by_container_type = {container_type: 0 for container_type in all_container_types}
        shop_packs_by_container_type = {container_type: 0 for container_type in all_container_types}
        user_packs = UserPacks.objects.filter(shop_id=shop_id).prefetch_related('containers')
        for user_pack in user_packs:
            for container in user_pack.containers.all():
                container_type = container.type
                loans_by_container_type[container_type] = loans_by_container_type.get(container_type, 0) + 1

        # Count shop containers by container type for the specific shop
        shop_containers = Container.objects.filter(shop_id=shop_id)
        for container in shop_containers:
            container_type = container.type
            shop_packs_by_container_type[container_type] = shop_packs_by_container_type.get(container_type, 0) + 1

        # Prepare response data with only counts
        response_data = {
            "loans_by_container_type": loans_by_container_type,
            "shop_packs_by_container_type": shop_packs_by_container_type,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='last-containers')
    def last_containers(self, request):
        try:
            # Fetch the last three shops (ordering by the 'id' field)
            last = UserPacks.objects.order_by('-id')[:10]
            serializer = NewUserPacksSerializer(last, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='returns')
    def returns(self, request):
        try:
            # Fetch all UserPacks, ordered by the 'id' field
            user_packs = UserPacks.objects.order_by('-id')

            final_data = []
            for user_pack in user_packs:
                # Get all containers associated with the UserPack
                containers = user_pack.containers.all()

                # Check if any container is a loan
                has_loans = any(container.is_loan for container in containers)
                if not has_loans:
                    # If there are loans, serialize the UserPack and append to final_data
                    serialized_data = NewUserPacksSerializer(user_pack).data
                    final_data.append(serialized_data)

            # If no loans found, you may want to return an empty list or a specific message
            if not final_data:
                return Response({"detail": "No loans found."}, status=status.HTTP_404_NOT_FOUND)

            return Response(final_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='loans')
    def loans(self, request):
        try:
            # Fetch all UserPacks, ordered by the 'id' field
            user_packs = UserPacks.objects.order_by('-id')

            final_data = []
            for user_pack in user_packs:
                # Get all containers associated with the UserPack
                containers = user_pack.containers.all()

                # Check if any container is a loan
                has_loans = any(container.is_loan for container in containers)
                print(has_loans)
                if has_loans:
                    # If there are loans, serialize the UserPack and append to final_data
                    serialized_data = NewUserPacksSerializer(user_pack).data
                    final_data.append(serialized_data)

            # If no loans found, you may want to return an empty list or a specific message
            if not final_data:
                return Response({"detail": "No loans found."}, status=status.HTTP_404_NOT_FOUND)

            return Response(final_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response
from .models import Container, ContainerRequest, Shop
from .serializers import ContainerSerializer, ContainerRequestSerializer


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ContainerRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContainerRequest.objects.all()
    serializer_class = ContainerRequestSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['status', 'shop']
    search_fields = ['shop__name']
