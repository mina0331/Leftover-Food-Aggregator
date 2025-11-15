from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile



# Create your views here.
@login_required
def select_role(request):
    # Staff/superusers shouldn't see role selection - they're automatically moderators
    if request.user.is_staff or request.user.is_superuser:
        profile, _ = Profile.objects.get_or_create(
            user=request.user,
            defaults={'has_seen_welcome': False}
        )
        if profile.role != Profile.Role.MODERATOR:
            profile.role = Profile.Role.MODERATOR
            profile.save()
        return redirect("userprivileges:moderator_home")
    
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'has_seen_welcome': False}
    )

    if profile.role:
        return redirect("my_profile")
    if (request.method == "POST"):
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("my_profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profilepage/edit_profile.html", {"form": form})

def my_profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'has_seen_welcome': False}
    )
    return render(request, "profilepage/profile.html", {"profile": profile})

@login_required
def post_login_redirect(request):
    # Staff/superusers should go to moderator dashboard (they have admin access)
    if request.user.is_staff or request.user.is_superuser:
        # Ensure they have moderator role in profile for consistency
        profile, _ = Profile.objects.get_or_create(
            user=request.user,
            defaults={'has_seen_welcome': False}
        )
        if profile.role != Profile.Role.MODERATOR:
            profile.role = Profile.Role.MODERATOR
            profile.save()
        return redirect("userprivileges:moderator_home")
    
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'has_seen_welcome': False}
    )
    
    # Check if this is a first-time user (just created OR hasn't seen welcome)
    if created or not profile.has_seen_welcome:
        return redirect("welcome_screen")
    
    if not profile.role:
        return redirect("select_role")
    return redirect("my_profile")

@login_required
def welcome_screen(request):
    """Show welcome screen to first-time users"""
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'has_seen_welcome': False}
    )
    
    if request.method == "POST":
        # User clicked "Get Started" - mark as seen and continue
        profile.has_seen_welcome = True
        profile.save()
        
        # Continue to role selection if they haven't chosen one yet
        if not profile.role:
            return redirect("select_role")
        return redirect("my_profile")
    
    # Show welcome page
    return render(request, "profilepage/welcome.html", {"profile": profile})

def profile_redirect(request):
    if request.user.is_authenticated:
        return redirect("my_profile")
    else:
        return redirect("account_login")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            remove = request.POST.get("remove_photo") == "1"
            prof = form.save(commit=False)

            # If remove requested, delete old file and clear field
            if remove and prof.profile_pic:
                prof.profile_pic.delete(save=False)
                prof.profile_pic = None

            prof.save()
            form.save_m2m()
            messages.success(request, "Profile updated.")
            return redirect("my_profile")
        else:
            messages.error(request, f"Fix errors: {form.errors}")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profilepage/edit_profile.html", {"form": form})


