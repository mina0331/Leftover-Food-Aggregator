
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

class Cuisine(models.TextChoices):
    KOREAN = "korean", "Korean"
    JAPANESE = "japanese", "Japanese"
    CHINESE = "chinese", "Chinese"
    AMERICAN = "american", "American"
    ITALIAN = "italian", "Italian"
    MEXICAN = "mexican", "Mexican"
    INDIAN = "indian", "Indian"
    THAI = "thai", "Thai"
    VIETNAMESE = "vietnamese", "Vietnamese"
    HALAL = "halal", "Halal"
    VEGAN = "vegan", "Vegan"
    BBQ = "bbq", "BBQ"
    SEAFOOD = "seafood", "Seafood"
    DESSERT = "dessert", "Dessert"
    OTHER = "other", "Other"

class Post(models.Model):
    event = models.TextField()
    event_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cuisine = models.CharField(max_length=20, choices=Cuisine.choices, default = Cuisine.OTHER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=event_image_upload_to, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} ({self.author})"

    def save(self, *args, **kwargs):
        if self.cuisine:
            self.cuisine = self.cuisine.lower()
            #making the cuisine choice case-insensitive
        super().save(*args, **kwargs)



