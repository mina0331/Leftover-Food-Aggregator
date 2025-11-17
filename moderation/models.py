from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class FlaggedContent(models.Model):
    """
    Generic model to flag any content (Messages, Posts, etc.)
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved (No Action)"
        DELETED = "deleted", "Content Deleted"
        DISMISSED = "dismissed", "Dismissed"
        EDITED = "edited", "Content Edited"
    
    # Generic foreign key to link to any model (Message, Post, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Who flagged it and why
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flags_submitted')
    reason = models.TextField(help_text="Reason for flagging this content")
    flagged_at = models.DateTimeField(auto_now_add=True)
    
    # Moderation details
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flags_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    moderator_notes = models.TextField(blank=True, help_text="Internal notes from moderator")
    
    class Meta:
        ordering = ['-flagged_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status', '-flagged_at']),
        ]
        verbose_name = "Flagged Content"
        verbose_name_plural = "Flagged Content"
    
    def __str__(self):
        content_str = str(self.content_object)[:50] if self.content_object else "Unknown"
        return f"Flag #{self.id}: {content_str} ({self.get_status_display()})"
    
    def get_content_type_name(self):
        """Get human-readable name of the content type"""
        return self.content_type.model_class()._meta.verbose_name.title()
    
    def approve(self, moderator, notes=""):
        """Approve the flagged content (dismiss the flag)"""
        self.status = self.Status.APPROVED
        self.reviewed_by = moderator
        self.reviewed_at = timezone.now()
        self.moderator_notes = notes
        self.save()
    
    def dismiss(self, moderator, notes=""):
        """Dismiss the flag (content is fine)"""
        self.status = self.Status.DISMISSED
        self.reviewed_by = moderator
        self.reviewed_at = timezone.now()
        self.moderator_notes = notes
        self.save()
    
    def delete_content(self, moderator, notes=""):
        """Delete the flagged content"""
        # Save flag status first, then delete content
        self.status = self.Status.DELETED
        self.reviewed_by = moderator
        self.reviewed_at = timezone.now()
        self.moderator_notes = notes
        # Save with update_fields to avoid GenericForeignKey issues
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'moderator_notes'])
        
        # Delete the content object after saving flag status
        if self.content_object:
            self.content_object.delete()
    
    def edit_content(self, moderator, notes=""):
        """Mark the flagged content as edited"""
        self.status = self.Status.EDITED
        self.reviewed_by = moderator
        self.reviewed_at = timezone.now()
        self.moderator_notes = notes
        self.save()


class UserSuspension(models.Model):
    """
    Track user suspensions for repeated violations
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suspensions')
    suspended_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suspensions_issued')
    reason = models.TextField(help_text="Reason for suspending this user")
    suspended_at = models.DateTimeField(auto_now_add=True)
    suspended_until = models.DateTimeField(null=True, blank=True, help_text="Leave empty for permanent suspension")
    is_active = models.BooleanField(default=True, help_text="Whether this suspension is currently active")
    reinstated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspensions_reinstated'
    )
    reinstated_at = models.DateTimeField(null=True, blank=True)
    reinstatement_notes = models.TextField(blank=True, help_text="Notes about why user was reinstated")
    
    class Meta:
        ordering = ['-suspended_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', '-suspended_at']),
        ]
        verbose_name = "User Suspension"
        verbose_name_plural = "User Suspensions"
    
    def __str__(self):
        duration = f"until {self.suspended_until.date()}" if self.suspended_until else "permanently"
        status = "Active" if self.is_active else "Reinstated"
        return f"{self.user.username} - {status} ({duration})"
    
    def is_expired(self):
        """Check if temporary suspension has expired"""
        if not self.suspended_until:
            return False  # Permanent suspension never expires
        return timezone.now() > self.suspended_until
    
    def reinstate(self, moderator, notes=""):
        """Reinstate the user (mark suspension as inactive)"""
        self.is_active = False
        self.reinstated_by = moderator
        self.reinstated_at = timezone.now()
        self.reinstatement_notes = notes
        self.save()
    
    def get_duration_display(self):
        """Get human-readable duration"""
        if not self.suspended_until:
            return "Permanent"
        if self.is_expired():
            return f"Expired (was until {self.suspended_until.date()})"
        return f"Until {self.suspended_until.date()}"
