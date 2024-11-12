from django.db import models
from account.models import *
from shop.models import *


class Container(models.Model):
    CONTAINER_TYPE_CHOICES = [
        ('DISH', 'Dish'),
        ('GLS', 'Glass'),
    ]
    CONTAINER_TYPE_NUMERICAL_CODES = {
        'DISH': 23,
        'GLS': 24,
    }
    CONTAINER_COUNTRY_NUMERICAL_CODE = {
        'UAE': 33,
        "OM": 44,
    }
    COUNTRY_TYPE_CHOICES = [
        ('UAE', '33'),
        ('OM', '44'),
    ]
    type = models.CharField(max_length=4,choices=CONTAINER_TYPE_CHOICES)
    code = models.CharField(max_length=12)
    guarantee_amount = models.IntegerField(default=15)
    country = models.CharField(max_length=3, choices=COUNTRY_TYPE_CHOICES , null=True)
    date = models.DateField(auto_now=True)
    shop = models.ForeignKey(Shop,null=True, on_delete=models.PROTECT)
    is_loan = models.BooleanField(default=False)




class ContainerRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='PENDING')
    approval_date = models.DateTimeField(null=True, blank=True)
    denial_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Request by {self.shop.name} (Status: {self.status})"

class ContainerItemRequest(models.Model):
    container_request = models.ForeignKey(ContainerRequest, related_name='items', on_delete=models.CASCADE)
    container_type = models.CharField(max_length=4, choices=Container.CONTAINER_TYPE_CHOICES, null=True)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.count} of {self.container_type}"


class UserPackInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE , related_name='pack_info')
    count = models.PositiveIntegerField(default=0)


class UserPacks(models.Model):
    user_pack_id = models.ForeignKey(UserPackInfo , on_delete=models.PROTECT)
    pack_description = models.TextField()
    given_date = models.DateTimeField()
    due_date = models.DateTimeField(null=True)
    containers_num = models.PositiveIntegerField(default=0)
    containers = models.ManyToManyField(Container)
    shop = models.ForeignKey(Shop , on_delete=models.PROTECT , null=True)

