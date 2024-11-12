from django.db import models

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible


@deconstructible
class FileValidator:
    def __init__(self, max_size=2 * 1024 * 1024, allowed_types=None):
        self.max_size = max_size
        self.allowed_types = allowed_types or ['image/jpeg', 'image/png']

    def __call__(self, file):
        # Check file size
        if file.size > self.max_size:
            raise ValidationError(f"File size should not exceed {self.max_size / (1024 * 1024)} MB.")

        # Check file type
        if file.content_type not in self.allowed_types:
            raise ValidationError(f"File type must be one of the following: {', '.join(self.allowed_types)}.")


# Apply validator to the logo field
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
    logo = models.ImageField(upload_to='shop_logos/' , validators=[FileValidator()])
    x_gis = models.FloatField(null=True)
    y_gis = models.FloatField(null=True)
    reset_code = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.name

