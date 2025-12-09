from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib.auth import logout
from .models import Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from Friendslist.models import Friend;
from posting.models import Post;
from userprivileges.roles import is_moderator



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
    
    # Prevent moderators from editing other users' profiles
    # They can only edit their own profile
    if request.method == "POST":
        # Check if trying to edit someone else's profile (shouldn't happen via normal flow, but check anyway)
        profile_id = request.POST.get('profile_id') or request.GET.get('profile_id')
        if profile_id and int(profile_id) != profile.id:
            if is_moderator(request.user) or request.user.is_staff:
                messages.error(request, "Moderators cannot edit other users' profiles.")
                return redirect("my_profile")
    
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

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    profile = getattr(profile_user, "profile", None)  # assuming OneToOne Profile
    is_friend = Friend.are_friends(request.user, profile_user)
    user_posts = (
        Post.objects
        .filter(author=profile_user, is_deleted=False)  # or whatever field you use
        .order_by('-created_at')
        .distinct()
    )
    context = {
        "profile_user": profile_user,
        "profile": profile,
        "is_friend": is_friend,
        "user_posts": user_posts,
    }
    return render(request, "profilepage/profile_viewable.html", context)

@login_required
def delete_account(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)

    # Prevent moderators from deleting ANY account (including their own)
    if is_moderator(request.user) or request.user.is_staff:
        messages.error(request, "Moderators cannot delete accounts. Please contact an administrator if you need to delete your account.")
        return redirect("my_profile")
    
    # Only allow deleting yourself (or let superuser manage others, but not moderators)
    if request.user != profile_user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete this account.")
        return redirect("my_profile")  # or whatever your profile url name is

    if request.method == "POST":
        # Deleting the User will also delete Profile because of on_delete=models.CASCADE
        logout(request)
        profile_user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("landingpage")  # update with your homepage url name

    # GET → show confirmation page
    return render(request, "profilepage/confirm_delete.html", {
        "profile_user": profile_user,
    })



