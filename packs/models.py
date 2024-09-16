from django.db import models
from account.models import *

class UserPackInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    count=models.PositiveIntegerField()

class UserPacks(models.Model):
    user_pack_id = models.ForeignKey(UserPackInfo , on_delete=models.PROTECT)
    pack_title = models.CharField(max_length=64)
    pack_description = models.TextField()
    given_date = models.DateField()
    due_date = models.DateField()
# Create your models here.
