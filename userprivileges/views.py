
# Create your views here.
# userprivileges/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .roles import is_student, is_provider, is_moderator

# Send users to their role-specific page after login
@login_required
def post_login_router(request):
    # Check staff/superuser first - they have admin access, treat as moderators
    if request.user.is_staff or request.user.is_superuser:
        # Ensure their profile has moderator role for consistency
        from profiles.models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.role != Profile.Role.MODERATOR:
            profile.role = Profile.Role.MODERATOR
            profile.save()
        return redirect("userprivileges:moderator_home")
    
    # Check moderator first (highest privilege)
    if is_moderator(request.user):
        return redirect("userprivileges:moderator_home")
    if is_provider(request.user):
        return redirect("userprivileges:provider_home")
    if is_student(request.user):
        return redirect("userprivileges:student_home")
    # No role yet? Send home (adjust if you have a role-select page)
    return redirect("landing:home")

# -------- Student-only page --------
@login_required
def student_home(request):
    # Allow moderators to access student view (for moderation/testing)
    if not (is_student(request.user) or is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        return redirect("userprivileges:provider_home")
    # Render the "available food" list that Students can see.
    # If you already have a FoodListing model elsewhere, you can import and query it.
    # For now, keep it simple; you can drop data here later.
    return render(request, "userprivileges/student_home.html")

# -------- Food Provider-only page --------
@login_required
def provider_home(request):
    # Allow moderators to access provider view (for moderation/testing)
    if not (is_provider(request.user) or is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        return redirect("userprivileges:student_home")
    # Provider sees a button to post food (wire to your real form later)
    return render(request, "userprivileges/provider_home.html")

# -------- Moderator-only page --------
@login_required
def moderator_home(request):
    # Allow access if user is moderator OR has staff/superuser status
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        return redirect("userprivileges:student_home")
    # Moderator sees admin dashboard, user management, content moderation tools
    return render(request, "userprivileges/moderator_home.html")