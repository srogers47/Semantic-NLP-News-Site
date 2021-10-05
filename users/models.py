from django.db import models
from django.contrib.auth.models import AbstractUser

class ExtendUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    # Name and email already provided in default model
    USERNAME_FIELD = "username"  
    EMAIL_FIELD = "email" 
