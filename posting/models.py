
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import get_valid_filename
from django.contrib.auth import get_user_model
User = get_user_model()
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



class Post(models.Model):
    event = models.TextField()
    event_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=event_image_upload_to, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} ({self.author})"

    def save(self, *args, **kwargs):
        if self.cuisine:
            self.cuisine.name = self.cuisine.name.lower()
            #making the cuisine choice case-insensitive
        super().save(*args, **kwargs)

class Report(models.Model):
    class Reason(models.TextChoices):
        SPOILED = "spoiled", "Spoiled / Rotten"
        EXPIRED = "expired", "Expired"
        ALLERGEN = "allergen", "Incorrect allergen info"
        HAZARD = "hazard", "Food safety hazard"
        OTHER = "other", "Other"
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reason = models.CharField(max_length=30, choices=Reason.choices)
    description = models.TextField(blank=True)  # optional freeform
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports_resolved")
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report #{self.id} on {self.post} by {self.reporter}"




