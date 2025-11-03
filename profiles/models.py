from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import get_valid_filename
import os
# Create your models here.

User = get_user_model()

def profile_pic_upload_to(instance, filename):
    base = get_valid_filename(os.path.basename(filename))
    return f"profile_pics/user_{instance.user.id}/{base}"


class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ORG = "org", "club"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, blank=True, null=True, default=None)
    display_name = models.CharField(max_length=120, blank = True)
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
