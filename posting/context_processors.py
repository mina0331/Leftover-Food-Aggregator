from .models import Post
from django.utils import timezone
from django.db.models import Q


def unread_posts_count(request):
    if not request.user.is_authenticated:
        return {}

    count = (
        Post.objects
        .filter(is_deleted=False)  
        .filter(
            Q(pickup_deadline__isnull=True) |
            Q(pickup_deadline__gt=timezone.now())
        )
        .exclude(read_users=request.user)  
        .count()
    )

    return {"unread_posts_count": count}
