from django.db import models
from account.models import *
from shop.models import *

class UserPackInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    count=models.PositiveIntegerField()

class UserPacks(models.Model):
    user_pack_id = models.ForeignKey(UserPackInfo , on_delete=models.PROTECT)
    pack_description = models.TextField()
    given_date = models.DateField()
    due_date = models.DateField()
    containers = models.PositiveIntegerField(default=0)
    shop = models.ForeignKey(Shop , on_delete=models.PROTECT , null=True)

