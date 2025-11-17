from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuisine, Post, OrganizerThank, Report
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from .forms import PostForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import ReportForm
import csv
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
# Create your views here.


def index(request):
    # search text
    q = request.GET.get("q", "").strip()

    # filters
    cuisine_id = request.GET.get("cuisine", "").strip()
    selected_org = request.GET.get("org", "").strip()
    date_order = request.GET.get("date_order", "newest").strip()  # 'newest' or 'oldest'

    post_list = Post.objects.filter(is_deleted=False)

    # Search across event, description, cuisine name, and org username
    if q:
        post_list = post_list.filter(
            Q(event__icontains=q) |
            Q(event_description__icontains=q) |
            Q(cuisine__name__icontains=q) |
            Q(author__username__icontains=q)
        )

    # Cuisine filter
    if cuisine_id:
        post_list = post_list.filter(cuisine_id=cuisine_id)

    # Organization filter
    if selected_org:
        post_list = post_list.filter(author__username=selected_org)

    # Date ordering
    if date_order == "oldest":
        post_list = post_list.order_by("created_at")
    else:
        post_list = post_list.order_by("-created_at")

    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    cuisines = Cuisine.objects.order_by("name")
    # org users that actually have posts, and whose profile role is 'org'
    orgs = User.objects.filter(
        profile__role='org',
        post__isnull=False
    ).distinct().order_by("username")

    return render(request, "posting/posts.html", {
        "posts": page_obj,
        "page_obj": page_obj,
        "total_posts": post_list.count(),
        "search_query": q,
        "cuisines": cuisines,
        "selected_cuisine_id": cuisine_id,
        "orgs": orgs,
        "selected_org": selected_org,
        "selected_date_order": date_order,
    })
def event_history(request):
    #Read-only list of past leftover food posts, newest first.
    #For now, 'history' just means all posts ordered by created_at.

    post_list = Post.objects.order_by("-created_at")
    paginator = Paginator(post_list, 10)   # 10 per page, adjust if you want
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "posting/event_history.html", {
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
        form = PostForm(request.POST, request.FILES)   # include files
        if form.is_valid():
            post = form.save(commit=False)             # set author
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created.')
            return redirect("posting:post_list")
        else:
            messages.error(request, 'Please fix some errors.')
    else:
        form = PostForm()

    # render on GET or invalid POST
    return render(request, "posting/create_post.html", {"form": form})

@login_required
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        # Post was deleted - check if it was deleted by moderation
        from moderation.models import FlaggedContent
        post_content_type = ContentType.objects.get_for_model(Post)
        deleted_flag = FlaggedContent.objects.filter(
            content_type=post_content_type,
            object_id=post_id,
            status=FlaggedContent.Status.DELETED
        ).first()
        
        if deleted_flag:
            messages.warning(request, 'This post has been removed by a moderator for violating community guidelines.')
        else:
            messages.info(request, 'This post no longer exists. It may have been deleted by the author.')
        
        return redirect('posting:post_list')
    
    # Check if post is soft-deleted
    if post.is_deleted:
        messages.info(request, 'This post has been deleted.')
        return redirect('posting:post_list')
    
    # Get content type for Post model (for flagging)
    post_content_type = ContentType.objects.get_for_model(Post)
    return render(request, "posting/post_detail.html", {
        "post": post,
        "post_content_type_id": post_content_type.id,
    })

@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        messages.warning(request, 'This post no longer exists and cannot be edited.')
        return redirect('posting:post_list')
    
    # Check if post is soft-deleted
    if post.is_deleted:
        messages.warning(request, 'This post has been deleted and cannot be edited.')
        return redirect('posting:post_list')
    
    if request.user != post.author:
        messages.warning(request, 'You do not have permission to edit this post.')
        return redirect('posting:post_detail', post_id=post_id)
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
            return redirect('posting:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "posting/edit_post.html", {"form": form, "post": post})

@login_required
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        messages.warning(request, 'This post no longer exists.')
        return redirect('posting:post_list')
    
    if request.user != post.author:
        messages.warning(request, 'You do not have permission to delete this post.')
        return redirect('posting:post_detail', post_id=post_id)
    
    if request.method == "POST":
        # SOFT DELETE — marking it deleted instead of removing from DB
        post.is_deleted = True
        post.save()
        messages.success(request, 'Your post has been deleted.')
        return redirect("posting:post_list")

    return render(request, "posting/delete_post.html", {"post": post})

@login_required
@require_POST
def thank_organizer(request):
    """
    Allow a logged-in user to thank an organizer.
    Returns JSON response with success/failure status.
    """
    organizer_id = request.POST.get('organizer_id')
    
    # Get the organizer user object
    organizer = get_object_or_404(User, id=organizer_id)
    
    try:
        # Attempt to create the thank relationship
        OrganizerThank.objects.create(
            thanker=request.user,
            organizer=organizer
        )
        
        # Get the updated count of thanks for this organizer
        thanks_count = organizer.thanks_received.count()
        
        return JsonResponse({
            'status': 'success',
            'thanks_count': thanks_count
        })
        
    except IntegrityError:
        # User has already thanked this organizer
        return JsonResponse({
            'status': 'already_thanked'
        })

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author:
        messages.warning(request, "You cannot report your own post.")
        return redirect("posting:post_detail", post_id=post.id)

    existing_report = Report.objects.filter(post=post, reporter=request.user).first()
    if existing_report:
        messages.info(request, "You already submitted a report for this post.")
        return redirect("posting:post_detail", post_id=post.id)

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(request, "Thank you — your report has been submitted and will be reviewed.")
            return redirect("posting:post_detail", post_id=post.id)
    else:
        form = ReportForm()

    return render(request, "posting/report_form.html", {
        "form": form,
        "post": post,
    })

@staff_member_required
def export_data(request):
    #Export anonymized data about posts as a CSV file.
    #Admin-only (staff).

    # Tell browser we are returning a CSV file
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="uva_leftovers_data.csv"'

    writer = csv.writer(response)

    # ---- Overall metrics ----
    total_posts = Post.objects.count()

    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total posts", total_posts])
    writer.writerow([])

    # ---- Posts by cuisine (anonymized: no user info) ----
    writer.writerow(["Cuisine", "Post count"])

    cuisine_counts = (
        Post.objects.values("cuisine__name")
        .annotate(count=Count("id"))
        .order_by("cuisine__name")
    )

    for row in cuisine_counts:
        writer.writerow([row["cuisine__name"], row["count"]])

    return response
