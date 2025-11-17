
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import get_valid_filename
from django.contrib.auth import get_user_model
User = get_user_model()
import time
import qrcode
from io import BytesIO
from django.core.files import File


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
    building_name = models.CharField(max_length=30)

    def __str__(self):
        return self.building_name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        PUBLISHED = "published", "Published"

    event = models.TextField()
    event_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PUBLISHED)
    publish_at = models.DateTimeField(null=True, blank=True)
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
    qr_code_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} ({self.author})"

    def save(self, *args, **kwargs):
        if self.cuisine:
            self.cuisine.name = self.cuisine.name.lower()
            #making the cuisine choice case-insensitive
        super().save(*args, **kwargs)

        # Generate QR code after saving so we have self.id
        if not self.qr_code_image:  # only generate if it doesn't exist
            self.generate_qr_code()
            super().save(update_fields=['qr_code_image'])

    def generate_qr_code(self):
        qr_data = f"Post ID: {self.id}, Event: {self.event}, Author: {self.author.username}"
    
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        blob = BytesIO()
        img.save(blob, 'PNG')
        
        self.qr_code_image.save(f'post_{self.id}_qr.png', File(blob), save=False)
        blob.close()

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



class OrganizerThank(models.Model):
    thanker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thanks_given')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thanks_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('thanker', 'organizer')

    def __str__(self):
        return f"{self.thanker.username} thanked {self.organizer.username}"
