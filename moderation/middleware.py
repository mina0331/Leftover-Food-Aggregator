from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from .models import UserSuspension
from userprivileges.roles import is_moderator


class SuspensionMiddleware:
    """
    Middleware to block suspended users from accessing the site
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for anonymous users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip check for staff/superusers/moderators (they can always access)
        if request.user.is_staff or request.user.is_superuser or is_moderator(request.user):
            return self.get_response(request)
        
        # Skip check for admin URLs
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Skip check for static/media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        
        # Skip check for suspension notice page itself (to avoid redirect loop)
        if request.path.startswith('/moderation/suspension-notice/'):
            return self.get_response(request)
        
        # Check if user is suspended
        active_suspension = UserSuspension.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if active_suspension:
            # Check if temporary suspension has expired
            if active_suspension.is_expired():
                # Auto-reinstate expired suspensions
                active_suspension.is_active = False
                active_suspension.save()
                return self.get_response(request)
            
            # Redirect to suspension notice page
            return redirect('moderation:suspension_notice', suspension_id=active_suspension.id)
        
        return self.get_response(request)

