from random import choices

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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


