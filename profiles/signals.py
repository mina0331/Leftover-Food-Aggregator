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
