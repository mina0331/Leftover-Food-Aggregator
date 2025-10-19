
# Create your views here.
# userprivileges/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .roles import is_student, is_provider

# Send users to their role-specific page after login
@login_required
def post_login_router(request):
    if is_provider(request.user):
        return redirect("userprivileges:provider_home")
    if is_student(request.user):
        return redirect("userprivileges:student_home")
    # No role yet? Send home (adjust if you have a role-select page)
    return redirect("landing:home")

# -------- Student-only page --------
@login_required
def student_home(request):
    if not is_student(request.user):
        return redirect("userprivileges:provider_home")
    # Render the "available food" list that Students can see.
    # If you already have a FoodListing model elsewhere, you can import and query it.
    # For now, keep it simple; you can drop data here later.
    return render(request, "userprivileges/student_home.html")

# -------- Food Provider-only page --------
@login_required
def provider_home(request):
    if not is_provider(request.user):
        return redirect("userprivileges:student_home")
    # Provider sees a button to post food (wire to your real form later)
    return render(request, "userprivileges/provider_home.html")