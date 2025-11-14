from django.db.models import Count, Q
from .models import Conversation

from chat.models import Message

def unread_messages(request):
    if not request.user.is_authenticated:
        return {}

    unread_count = (
        Message.objects
        .filter(
            conversation__participants=request.user,  # I'm in the convo
            is_read=False                             # message not read yet
        )
        .exclude(sender=request.user)                 # don’t count my own msgs
        .count()
    )

    return {"unread_count": unread_count}
