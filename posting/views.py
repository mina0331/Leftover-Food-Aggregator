from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuisine, Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib import messages
# Create your views here.


def index(request):
    post_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(post_list, 5)  # 5 posts per page

    page_number = request.GET.get('page')   # e.g. ?page=2
    page_obj = paginator.get_page(page_number)

    return render(request, 'posting/posts.html', {'page_obj': page_obj})



@login_required
def create_post(request):
    if request.user.profile.role != 'org':
        messages.warning(request, 'You are not authorized to create posts.')
        return redirect('posting:post_list')
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)   # include files
        if form.is_valid():
            post = form.save(commit=False)             # set author
            post.author = request.user
            post.save()
            return redirect("posting:post_list")       # or your desired route
    else:
        form = PostForm()

    # render on GET or invalid POST
    return render(request, "posting/create_post.html", {"form": form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
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
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "posting/edit_post.html", {"form": form, "post": post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('post_detail', post_id=post_id)
    if request.method == "POST":
        # remove image from storage first (S3/local)
        if post.image:
            post.image.delete(save=False)
        post.delete()
        return redirect("posts")  # go back to list

        # GET: render a confirmation page
    return render(request, "posting/delete_post.html", {"post": post})

