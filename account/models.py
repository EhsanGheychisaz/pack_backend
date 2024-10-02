from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    name = models.CharField(max_length=128)
    is_deleted = models.BooleanField(default=False)
    phone = models.CharField(max_length=18 , unique=True , null=True)
    email = models.EmailField(null=True)
    created_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name


class UserAdmin(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField()
    password = models.CharField(max_length=256)

    def __str__(self):
        return self.name



class SecretKeyUser(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    key = models.CharField(max_length=528)

class SMSComfirmCode(models.Model):
    code = models.CharField(max_length=6)
    generated_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
