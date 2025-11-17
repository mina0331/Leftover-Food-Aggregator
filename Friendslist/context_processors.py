from Friendslist.models import FriendRequest
from chat.models import Message

def pending_friend_requests_count(request):
    if not request.user.is_authenticated:
        return {}

    pending_friend_requests = FriendRequest.objects.filter(
        status='pending', to_user=request.user
    ).count

    return {'pending_friend_requests_count': pending_friend_requests}
