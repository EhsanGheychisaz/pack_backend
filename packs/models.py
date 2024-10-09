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
    code = models.CharField(max_length=8)
    guarantee_amount = models.IntegerField(default=15)
    country = models.CharField(max_length=3, choices=COUNTRY_TYPE_CHOICES , null=True)
    date = models.DateField(auto_now=True)
    shop = models.ForeignKey(Shop,null=True, on_delete=models.PROTECT)


class UserPackInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    count = models.PositiveIntegerField()


class UserPacks(models.Model):
    user_pack_id = models.ForeignKey(UserPackInfo , on_delete=models.PROTECT)
    pack_description = models.TextField()
    given_date = models.DateTimeField()
    due_date = models.DateTimeField()
    containers_num = models.PositiveIntegerField(default=0)
    containers = models.ManyToManyField(Container)
    shop = models.ForeignKey(Shop , on_delete=models.PROTECT , null=True)

