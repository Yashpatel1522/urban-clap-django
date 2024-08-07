from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# yashvachhani


class User(AbstractUser):
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    profile_updated_at = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=100, null=True)


class UserProfiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name="profile")
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True)
