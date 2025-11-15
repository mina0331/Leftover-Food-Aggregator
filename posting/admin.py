from django.contrib import admin
from .models import Cuisine, Allergen

# Register your models here.
admin.site.register(Cuisine)
admin.site.register(Allergen)
