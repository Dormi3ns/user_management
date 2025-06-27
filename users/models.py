from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    is_locked = models.BooleanField(default=False)
    first_login = models.BooleanField(default=True)
