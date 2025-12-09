from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FlaggedContent, ModeratorNotification
from userprivileges.roles import is_moderator
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=FlaggedContent)
def create_moderator_notifications(sender, instance, created, **kwargs):
    """
    Automatically create notifications for all moderators when a new flag is created
    """
    if created and instance.status == FlaggedContent.Status.PENDING:
        # Get all moderators
        from profiles.models import Profile
        
        # Get users with moderator role in profile
        moderator_profiles = Profile.objects.filter(role=Profile.Role.MODERATOR).select_related('user')
        moderator_users = [profile.user for profile in moderator_profiles]
        
        # Also get staff/superusers (they are also moderators)
        staff_users = User.objects.filter(is_staff=True).distinct()
        
        # Combine and deduplicate
        all_moderators = set(list(moderator_users) + list(staff_users))
        
        # Create notifications for each moderator
        notifications = []
        for moderator in all_moderators:
            # Check if notification already exists (shouldn't, but just in case)
            if not ModeratorNotification.objects.filter(
                moderator=moderator,
                flagged_content=instance
            ).exists():
                notifications.append(
                    ModeratorNotification(
                        moderator=moderator,
                        flagged_content=instance,
                        is_read=False
                    )
                )
        
        # Bulk create notifications
        if notifications:
            ModeratorNotification.objects.bulk_create(notifications)

