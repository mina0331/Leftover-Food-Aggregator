from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'display_name']
    list_filter = ['role']
    search_fields = ['user__username', 'display_name']
