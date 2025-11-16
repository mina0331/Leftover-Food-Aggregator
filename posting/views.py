from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuisine, Post, Location
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib import messages
import json
from django.urls import reverse
import math

# Create your views here.

def index(request):
    post_list = Post.objects.order_by("-created_at")
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "posting/posts.html", {
        "posts": page_obj,
        "page_obj": page_obj,
        "total_posts": post_list.count(),
    })

@login_required
def create_post(request):
    if request.user.profile.role != 'org':
        messages.warning(request, 'You are not authorized to create posts.')
        return redirect('posting:post_list')

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.location is already set from the form's dropdown
            post.save()
            messages.success(request, 'Your post has been created.')
            return redirect("posting:post_list")
        else:
            messages.error(request, 'Please fix some errors.')
    else:
        form = PostForm()

    return render(request, "posting/create_post.html", {"form": form})
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.read_users.add(request.user)
    return render (request,"posting/post_detail.html", {"post": post})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('post_detail', post_id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            remove = request.POST.get("remove")
            if remove:
                # if the user clicked "remove image", delete old one
                if post.image:
                    post.image.delete(save=False)
                    post.image = None
            form.save()
            post.read_users.clear()
            return redirect('posting:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "posting/edit_post.html", {"form": form, "post": post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_read_users = post.read_users.all()
    if request.user != post.author:
        return redirect('post_detail', post_id=post_id)
    if request.method == "POST":
        # remove image from storage first (S3/local)
        if post.image:
            post.image.delete(save=False)
        post.delete()
        post.read_users.clear()
        return redirect("posting:post_list")  # go back to list

        # GET: render a confirmation page
    return render(request, "posting/delete_post.html", {"post": post})


def post_map(request):
    # Only posts that actually have a location with coordinates
    posts = (
        Post.objects
        .select_related("location")
        .filter(
            location__isnull=False,
            location__latitude__isnull=False,
            location__longitude__isnull=False,
        )
    )

    posts_data = []
    for p in posts:
        posts_data.append({
            "id": p.id,
            "event": p.event,  # use p.title if your field is named differently
            "building": p.location.building_name,
            "lat": p.location.latitude,
            "lng": p.location.longitude,
            "detail_url": reverse("posting:post_detail", args=[p.id]),
        })

    context = {
        "posts_json": json.dumps(posts_data),
    }
    return render(request, "posting/post_map.html", context)

def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def post_list(request):
    qs = (
        Post.objects
        .select_related("location", "cuisine")
        .all()
        .order_by("-created_at")
    )

    sort = request.GET.get("sort")
    user_lat = request.GET.get("lat")
    user_lng = request.GET.get("lng")
    selected_cuisine_id = request.GET.get("cuisine")  # this will be a string

    # 1) Filter by cuisine, if selected
    if selected_cuisine_id:
        qs = qs.filter(cuisine_id=selected_cuisine_id)

    posts = list(qs)

    # 2) Optional distance sorting
    if sort == "distance" and user_lat and user_lng:
        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)

            for p in posts:
                loc = p.location
                if loc and loc.latitude is not None and loc.longitude is not None:
                    p.distance_km = haversine_distance_km(
                        user_lat, user_lng, loc.latitude, loc.longitude
                    )
                else:
                    p.distance_km = None

            posts.sort(key=lambda p: p.distance_km if p.distance_km is not None else 1e9)
        except ValueError:
            pass

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj.object_list,
        "page_obj": page_obj,
        "sort": sort,
        "selected_cuisine_id": selected_cuisine_id,
        "cuisine_list": Cuisine.objects.all().order_by("name"),
    }
    return render(request, "posting/posts.html", context)