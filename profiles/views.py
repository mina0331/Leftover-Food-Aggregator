from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile



# Create your views here.
@login_required
def select_role(request):
    # Staff/superusers shouldn't see role selection - they're automatically moderators
    if request.user.is_staff or request.user.is_superuser:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.role != Profile.Role.MODERATOR:
            profile.role = Profile.Role.MODERATOR
            profile.save()
        return redirect("userprivileges:moderator_home")
    
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role:
        return redirect("my_profile")
    if (request.method == "POST"):
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("my_profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profilepage/select_role.html", {"form": form})

def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profilepage/profile.html", {"profile": profile})

@login_required
def post_login_redirect(request):
    # Staff/superusers should go to moderator dashboard (they have admin access)
    if request.user.is_staff or request.user.is_superuser:
        # Ensure they have moderator role in profile for consistency
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.role != Profile.Role.MODERATOR:
            profile.role = Profile.Role.MODERATOR
            profile.save()
        return redirect("userprivileges:moderator_home")
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.role:
        return redirect("select_role")
    return redirect("my_profile")

def profile_redirect(request):
    if request.user.is_authenticated:
        return redirect("my_profile")
    else:
        return redirect("account_login")