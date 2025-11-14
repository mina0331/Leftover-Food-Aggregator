from Friendslist.models import Friend
from chat.models import Message

def pending_friend_requests_count(request):
    if not request.user.is_authenticated:
        return {}

    pending_friend_requests = Message.objects.filter(
        status='pending', to_user=request.user
    ).count

    return {'pending_friend_requests_count': pending_friend_requests}
