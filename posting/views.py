from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuisine, Post, Location
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib import messages
import requests
from django.conf import settings

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

@login_required
def create_location(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            search_text = location.location_name

            url = "https://api.mapbox.com/search/geocode/v6/forward"
            params = {
                "q": search_text,
                "access_token": settings.MAPBOX_API_KEY
            }

            response = requests.get(url, params=params)
            data = response.json()

            # Extract coordinates
            try:
                feature = data["features"][0]
                coords = feature["geometry"]["coordinates"]
                lng, lat = coords[0], coords[1]

                location.latitude = lat
                location.longitude = lng

            except (KeyError, IndexError):
                # handle no result found
                location.latitude = None
                location.longitude = None

            location.save()
            return redirect("posts:list")
    else:
        form = LocationForm()

    return render(request, "locations/create.html", {"form": form})

