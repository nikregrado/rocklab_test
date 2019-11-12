from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserProfile(AbstractUser):
    # name = models.CharField(max_length=100)
    # surmane = models.CharField(max_length=100)
    is_blogger = models.BooleanField(default=False)
    is_reader = models.BooleanField(default=False)


class Hobby(models.Model):
    title = models.CharField(max_length=40)

    def __str__(self):
        return self.title


class Blogger(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True, related_name='blogger')
    birth_day = models.DateField()
    country = models.CharField(max_length=100)
    hobbies = models.ManyToManyField(Hobby)


class Interest(models.Model):
    title = models.CharField(max_length=40)

    def __str__(self):
        return self.title


class Reader(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True, related_name='reader')
    interests = models.ManyToManyField(Interest)
    status = models.CharField(max_length=255)
