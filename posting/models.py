
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import get_valid_filename
import time

# Create your models here.


def event_image_upload_to(instance, filename):
    base = get_valid_filename(filename)
    safe_event = get_valid_filename(instance.event)
    stamp = int(time.time())
    return f"events/{safe_event}/{instance.author.id}/{stamp}_{base}"

class Cuisine(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Allergen(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=30)

    def __str__(self):
        return self.location_name


class Post(models.Model):
    event = models.TextField()
    event_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=event_image_upload_to, null=True, blank=True)
    read_users = models.ManyToManyField(User, related_name="read_posts", blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} ({self.author})"

    def save(self, *args, **kwargs):
        if self.cuisine:
            self.cuisine.name = self.cuisine.name.lower()
            #making the cuisine choice case-insensitive
        super().save(*args, **kwargs)



