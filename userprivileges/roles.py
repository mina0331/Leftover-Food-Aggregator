# userprivileges/roles.py
from django.contrib.auth import get_user_model
from profiles.models import Profile  # ← your Profile with Role enum

User = get_user_model()

def has_profile(user):
    return getattr(user, "profile", None) is not None

def is_student(user):
    return (
        user.is_authenticated
        and has_profile(user)
        and user.profile.role == Profile.Role.STUDENT  # 'student'
    )

def is_provider(user):
    return (
        user.is_authenticated
        and has_profile(user)
        and user.profile.role == Profile.Role.ORG      # 'org' (club)
    )