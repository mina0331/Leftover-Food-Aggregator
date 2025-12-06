from django.shortcuts import render, redirect, get_object_or_404
from .models import Cuisine, Post, Location, OrganizerThank, RSVP, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from .forms import PostForm, RSVPForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.utils import timezone
import csv
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
import json
from django.urls import reverse
import math
from django.db.models import Q, F, FloatField, ExpressionWrapper
from django.db.models.functions import Power
from datetime import timedelta
from django.http import Http404
from Friendslist.models import Friend
from django.http import Http404
from Friendslist.models import Friend


two_days_ago = timezone.now() - timedelta(days=2)

def apply_visibility_filter(qs, user):
    if not user.is_authenticated:
        return qs.filter(visibility=Post.Visibility.PUBLIC)

    # Staff/admin → see everything
    if user.is_staff or user.is_superuser:
        return qs

    # Authenticated normal user → use Friend model
    friends = Friend.get_friends(user)

    return qs.filter(
        Q(visibility=Post.Visibility.PUBLIC)
        | Q(author=user)
        | Q(visibility=Post.Visibility.FRIENDS_ONLY, author__in=friends)
    )


def user_can_view_post(user, post):
    # Deleted posts shouldn't be visible at all
    if post.is_deleted:
        return False

    # Staff/admin → can always view
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        return True

    # Public posts
    if post.visibility == Post.Visibility.PUBLIC:
        # If published → visible to everyone
        if post.status == Post.Status.PUBLISHED:
            return True
        # Draft/scheduled → only author
        if user.is_authenticated and post.author == user:
            return True
        return False

    # Friends-only posts
    if not user.is_authenticated:
        return False

    # Author always sees their own post
    if post.author == user:
        return True

    # Check friendship
    friends = Friend.get_friends(user)
    return friends.filter(id=post.author_id).exists()

def index(request):
    # search text
    q = request.GET.get("q", "").strip()

    # filters
    cuisine_id = request.GET.get("cuisine", "").strip()
    selected_org = request.GET.get("org", "").strip()
    date_order = request.GET.get("date_order", "newest").strip()  # 'newest' or 'oldest'
    sort = request.GET.get("sort", "").strip()                    # '' or 'distance'
    lat_param = request.GET.get("lat")
    lng_param = request.GET.get("lng")

    # Start with published posts that are not deleted and not expired 
    qs = (
    Post.objects.filter(
        status=Post.Status.PUBLISHED,
        is_deleted=False,
        created_at__gte=two_days_ago
    ).filter(
    Q(pickup_deadline__isnull=True) | Q(pickup_deadline__gt=timezone.now())
    ).select_related("cuisine", "author")
    )

    # Search across event, description, cuisine name, and org username
    if q:
        qs = qs.filter(
            Q(event__icontains=q) |
            Q(event_description__icontains=q) |
            Q(cuisine__name__icontains=q) |
            Q(author__username__icontains=q)
        )

    # Cuisine filter
    if cuisine_id:
        qs = qs.filter(cuisine_id=cuisine_id)

    # Organization filter
    if selected_org:
        qs = qs.filter(author__username=selected_org)

    #distance ordering 
    # distance ordering 
    if sort == "distance" and lat_param and lng_param:
        try:
            user_lat = float(lat_param)
            user_lng = float(lng_param)

            qs = qs.annotate(
                distance=ExpressionWrapper(
                    Power(F("location__latitude") - user_lat, 2) +
                    Power(F("location__longitude") - user_lng, 2),
                    output_field=FloatField(),
                )
            ).order_by("distance")
        except ValueError:
            # If lat/lng are invalid, fall back to date ordering below
            sort = ""   # force it to behave like "no distance sort"

# Date ordering (only if NOT distance)
    if sort != "distance":
        if date_order == "oldest":
            qs = qs.order_by("created_at")
        else:
            qs = qs.order_by("-created_at")        

    qs = apply_visibility_filter(qs, request.user)

    paginator = Paginator(qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    

    cuisines = Cuisine.objects.filter(
        post__isnull=False
    ).distinct().order_by("name")
    
    # org users that actually have posts, and whose profile role is 'org'
    orgs = User.objects.filter(
        profile__role='org',
        post__isnull=False
    ).distinct().order_by("username")

    

    return render(request, "posting/posts.html", {
        "posts": page_obj,
        "page_obj": page_obj,
        "total_posts": qs.count(),
        "search_query": q,
        "cuisines": cuisines,
        "selected_cuisine_id": cuisine_id,
        "orgs": orgs,
        "selected_org": selected_org,
        "selected_date_order": date_order,
        "sort": sort,  
    })

def event_history(request): 
    # Start with all posts, newest first, excluding soft-deleted
    qs = Post.objects.filter(is_deleted=False).order_by("-created_at")

    # Apply the same visibility rules we use elsewhere
    qs = apply_visibility_filter(qs, request.user)

    paginator = Paginator(qs, 10)   # 10 per page, same as before
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "posting/event_history.html", {
        "posts": page_obj,
        "page_obj": page_obj,
        "total_posts": qs.count(),
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
            
            # Set status based on whether publish_at is provided
            if post.publish_at:
                post.status = Post.Status.SCHEDULED
                messages.success(request, f'Your post has been scheduled for {post.publish_at.strftime("%B %d, %Y at %I:%M %p")}.')
            else:
                post.status = Post.Status.PUBLISHED
                messages.success(request, 'Your post has been created.')
            
            post.save()
            return redirect("posting:post_list")
        else:
            # Debug: show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            messages.error(request, 'Please fix some errors.')
    else:
        form = PostForm()

    return render(request, "posting/create_post.html", {"form": form})
@login_required
def post_detail(request, post_id):
    try:
        post = Post.objects.select_related('cuisine', 'author').get(id=post_id)
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
    
    if not user_can_view_post(request.user, post):
        # Hide existence from unauthorized users
        raise Http404("Post not found")
    
    # Track read users
    if request.user.is_authenticated:
        post.read_users.add(request.user)
    
    # Get RSVP information
    user_rsvp = None
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(post=post, user=request.user, is_cancelled=False).first()
    
    # Get active RSVPs for post author
    active_rsvps = []
    if request.user == post.author:
        active_rsvps = RSVP.objects.filter(
            post=post,
            is_cancelled=False
        ).select_related('user', 'user__profile').order_by('created_at')
    
    # Get content type for Post model (for flagging)
    post_content_type = ContentType.objects.get_for_model(Post)
    return render(request, "posting/post_detail.html", {
        "post": post,
        "post_content_type_id": post_content_type.id,
        "user_rsvp": user_rsvp,
        "active_rsvps": active_rsvps,
        "rsvp_count": RSVP.objects.filter(post=post, is_cancelled=False).count(),
    })

@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.select_related('cuisine', 'author').get(id=post_id)
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
            post.read_users.clear()
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
        # Clear read users when post is deleted
        post.read_users.clear()
        messages.success(request, 'Your post has been deleted.')
        return redirect("posting:post_list")

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
            is_deleted=False,
            created_at__gte=two_days_ago,
        )
        .filter(
            Q(pickup_deadline__isnull=True) | Q(pickup_deadline__gt=timezone.now())
            )
    )

    posts = apply_visibility_filter(posts, request.user)

    posts_data = []
    for p in posts:
        posts_data.append({
            "id": p.id,
            "event": p.event,
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

@login_required
def create_rsvp(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if not user_can_view_post(request.user, post):
        raise Http404("Post not found")
    
    if request.user == post.author:
        messages.warning(request, "You cannot RSVP to your own post.")
        return redirect('posting:post_detail', post_id=post_id)
    
    if not post.is_pickup_available():
        messages.error(request, "Sorry, the pickup deadline for this post has passed.")
        return redirect('posting:post_detail', post_id=post_id)
    
    existing_rsvp = RSVP.objects.filter(post=post, user=request.user, is_cancelled=False).first()
    if existing_rsvp:
        messages.info(request, "You already have an active RSVP for this post.")
        return redirect('posting:post_detail', post_id=post_id)
    
    if request.method == "POST":
        form = RSVPForm(request.POST)
        if form.is_valid():
            rsvp = form.save(commit=False)
            rsvp.post = post
            rsvp.user = request.user
            
            estimated_arrival = rsvp.get_estimated_arrival_time()
            if post.pickup_deadline and estimated_arrival > post.pickup_deadline:
                messages.warning(
                    request,
                    f'Warning: Your estimated arrival time ({estimated_arrival.strftime("%I:%M %p")}) is after the pickup deadline ({post.pickup_deadline.strftime("%I:%M %p")}). '
                    'Food may not be available when you arrive.'
                )
            
            rsvp.save()

            # 🔔 Create in-app notification for the org / post author
            org_user = post.author
            profile = getattr(org_user, "profile", None)
            if profile and profile.role == "org":
                Notification.objects.create(
                    user=org_user,
                    post=post,
                    rsvp=rsvp,
                    message=(
                        f"{request.user.profile.display_name} RSVP’d to your post "
                        f"“{post.event}” and plans to arrive in {rsvp.estimated_arrival_minutes} minutes."
                    ),
                )

            messages.success(
                request,
                f'RSVP created! You indicated you will arrive in {rsvp.estimated_arrival_minutes} minutes. '
                'Please note: food is not guaranteed if you arrive late.'
            )
            return redirect('posting:post_detail', post_id=post_id)
    else:
        form = RSVPForm()
    
    return render(request, "posting/create_rsvp.html", {
        "form": form,
        "post": post,
    })

@login_required
def cancel_rsvp(request, rsvp_id):
    """Cancel an RSVP"""
    rsvp = get_object_or_404(RSVP, id=rsvp_id)
    
    # Only allow the user who created the RSVP to cancel it
    if rsvp.user != request.user:
        messages.error(request, "You don't have permission to cancel this RSVP.")
        return redirect('posting:post_detail', post_id=rsvp.post.id)
    
    if rsvp.is_cancelled:
        messages.info(request, "This RSVP is already cancelled.")
        return redirect('posting:post_detail', post_id=rsvp.post.id)
    
    if request.method == "POST":
        rsvp.cancel()
        messages.success(request, "Your RSVP has been cancelled.")
        return redirect('posting:post_detail', post_id=rsvp.post.id)
    
    return render(request, "posting/cancel_rsvp.html", {
        "rsvp": rsvp,
    })


@login_required
def view_post_rsvps(request, post_id):
    """View all RSVPs for a post (post author only)"""
    post = get_object_or_404(Post, id=post_id)
    
    # Only post author can view RSVPs
    if request.user != post.author:
        messages.error(request, "You don't have permission to view RSVPs for this post.")
        return redirect('posting:post_detail', post_id=post_id)
    
    active_rsvps = RSVP.objects.filter(
        post=post,
        is_cancelled=False
    ).select_related('user', 'user__profile').order_by('created_at')
    
    cancelled_rsvps = RSVP.objects.filter(
        post=post,
        is_cancelled=True
    ).select_related('user', 'user__profile').order_by('-cancelled_at')
    
    return render(request, "posting/view_rsvps.html", {
        "post": post,
        "active_rsvps": active_rsvps,
        "cancelled_rsvps": cancelled_rsvps,
    })


@login_required
def notification_inbox(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related("post", "rsvp").order_by("-created_at")

    # Mark all unread as read once user visits inbox
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, "posting/notification_inbox.html", {"notifications": notifications})

