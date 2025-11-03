from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def update_staff_status_on_role_change(sender, instance, created, **kwargs):
    """
    Automatically grant Django admin access (is_staff) to moderators.
    Remove staff access if they're no longer a moderator.
    This ensures moderators have the same access as admin users.
    """
    user = instance.user
    is_moderator = instance.role == Profile.Role.MODERATOR
    
    # Grant staff access to moderators (allows admin panel access)
    if is_moderator and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])
    # Remove staff access if they're no longer a moderator
    # But preserve if they're a superuser (superusers have both)
    elif not is_moderator and user.is_staff and not user.is_superuser:
        user.is_staff = False
        user.save(update_fields=['is_staff'])

@receiver(user_logged_in)
def update_profile_from_google(sender, request, user, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=user)
    sa = SocialAccount.objects.filter(user=user, provider="google").first()
    if sa:
        data = sa.extra_data
        profile.display_name = data["name"]
        profile.email = data["email"]

    profile.save()

@receiver(user_logged_in)
def ensure_user_logged_in(sender, request, user, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.role:
        request.session["needs_role_selection"] = True
