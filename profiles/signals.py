from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from .models import Profile

User = get_user_model()
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, user, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(sender=User)
def update_profile_from_google(sender, instance, created, **kwargs):
    profile = Profile.objects.get(user=instance)
    sa = SocialAccount.objects.filter(user=User, provider="google").first()
    if sa:
        data = sa.extra_data
        profile.display_name = data["display_name"]
    profile.save()
