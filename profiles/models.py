from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import get_valid_filename
import os,time
from django.templatetags.static import static
from posting.models import Cuisine, Allergen
# Create your models here.

User = get_user_model()

def profile_pic_upload_to(instance, filename):
    base = get_valid_filename(os.path.basename(filename))
    stamp = int(time.time())
    return f"profile_pics/user_{instance.user.id}/{time}_{base}"


class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ORG = "org", "club"
        MODERATOR = "moderator", "Moderator"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, blank=False, null=False, default=Role.STUDENT)
    display_name = models.CharField(max_length=120, blank = True)
    profile_pic = models.ImageField(upload_to=profile_pic_upload_to, blank=True, null=True)
    preferences = models.ManyToManyField(Cuisine, blank=True, related_name="profiles")
    allergens = models.ManyToManyField(Allergen, blank=True, related_name="profiles")
    has_seen_welcome = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def avatar_url(self):
        name = str(self.profile_pic or "")
        if name.startswith("http://") or name.startswith("https://"):
            return name  # external URL (Google)
        if self.profile_pic:
            return self.profile_pic.url  # managed file (S3/local)
        return static("images/default-avatar.png")  # fallback

    def is_suspended(self):
        """Check if user has an active suspension"""
        from moderation.models import UserSuspension
        active_suspension = UserSuspension.objects.filter(
            user=self.user,
            is_active=True
        ).first()
        
        if not active_suspension:
            return False
        
        # Check if temporary suspension has expired
        if active_suspension.is_expired():
            # Auto-reinstate expired suspensions
            active_suspension.is_active = False
            active_suspension.save()
            return False
        
        return True
    
    def save(self, *args, **kwargs):
        try:
            old = Profile.objects.get(pk=self.pk)
            if old.profile_pic and old.profile_pic != self.profile_pic:
                old.profile_pic.delete(save=False)
        except Profile.DoesNotExist:
            pass
        super().save(*args, **kwargs)
