from .models import Post
from django.utils import timezone
from django.db.models import Q
from .models import Notification
from datetime import timedelta

two_days_ago = timezone.now() - timedelta(days=2)

def unread_posts_count(request):
    if not request.user.is_authenticated:
        return {}

    count = (
        Post.objects
        .filter
        (is_deleted=False,
         status=Post.Status.PUBLISHED,
         created_at__gte=two_days_ago
        ).filter(
            Q(pickup_deadline__isnull=True) |
            Q(pickup_deadline__gt=timezone.now())
        )
        .exclude(read_users=request.user)  
        .count()
    )

    return {"unread_posts_count": count}

def rsvp_notifications(request):
    if not request.user.is_authenticated:
        return {}

    unread = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at")[:5]

    return {
        "rsvp_notifications": unread,
        "notification_count": unread.count(),  # 👍 simpler & more efficient
    }

