from django.shortcuts import render, redirect
from .models import Cuisine, Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
# Create your views here.


def index(request):
    posts = Post.objects.all()
    return render(request, "posting/posts.html", {"posts": posts})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
        else:
            form = PostForm()
        return render(request, "create_post.html", {"form": form})
