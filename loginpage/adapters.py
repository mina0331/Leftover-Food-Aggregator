# accounts/adapters.py
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        If a user tries to sign in with Google and a local account with the same
        (verified) email already exists, link the Google account to that user
        and proceed — skipping the 'existing email' blocking page.
        """
        # Already linked? Nothing to do.
        if sociallogin.is_existing:
            return

        data = sociallogin.account.extra_data or {}
        email = (data.get("email") or "").strip().lower()
        # Google sends 'email_verified' (OIDC). Older flows may use 'verified_email'.
        email_verified = bool(data.get("email_verified") or data.get("verified_email"))

        if not email or not email_verified:
            # Fall back to default flow if we can't trust the email.
            return

        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # No existing local user — allow normal auto-signup to create one.
            return

        # Link Google to the existing user and continue the login.
        sociallogin.connect(request, user)
