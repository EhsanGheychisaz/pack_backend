from django.db import models


from django.db import models

class Shop(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12)
    password = models.CharField(max_length=128)  # Store hashed password
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')
    logo = models.ImageField(upload_to='shop_logos/')
    x_gis = models.FloatField(null=True)
    y_gis = models.FloatField(null=True)
    reset_code = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.name

