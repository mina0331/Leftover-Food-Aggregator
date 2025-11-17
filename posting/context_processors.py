
from .models import Post

def unread_posts_count(request):
    if not request.user.is_authenticated:
        return {}

    # posts this user has NOT read yet
    count = Post.objects.exclude(read_users=request.user).count()

    return {"unread_posts_count": count}
