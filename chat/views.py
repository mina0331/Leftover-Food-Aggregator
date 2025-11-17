from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Case, When, IntegerField
from django.contrib.contenttypes.models import ContentType
from .models import Message
from .models import Friend
from .models import FriendRequest, Conversation
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Max



# Create your views here.
@login_required
def messages_index(request):
    # All conversations the user is part of, with last message time
    qs = (
        request.user.conversations
        .annotate(last_time=Max('messages__timestamp'))
        .order_by('-last_time')
    )

    # If they have at least one conversation, go to the most recent one
    latest = qs.first()
    if latest and latest.last_time is not None:
        return redirect('chat:conversation', convo_id=latest.id)

    # No conversations yet → show a simple placeholder page
    return render(request, 'chat/index.html', {
        'conversations': [],
    })
@login_required
def conversation_detail(request, convo_id):
    # 1) Get the conversation the user is part of
    conversation = get_object_or_404(
        Conversation,
        id=convo_id,
        participants=request.user
    )

    # 2) All messages in this conversation
    messages_qs = conversation.messages.select_related("sender").all()

    conversation.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    # 3) For 1:1 chat, figure out the "other_user"
    other_user = None
    if not conversation.is_group:
        other_user = conversation.participants.exclude(id=request.user.id).select_related("profile").first()

    # 4) Handle sending a new message
    if request.method == "POST":
        content = (request.POST.get("message") or "").strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
        return redirect("chat:conversation", convo_id=conversation.id)

    # Sidebar conversations list (all conversations this user is in)
    all_conversations = (
        request.user.conversations
        .all()
        .prefetch_related("participants", "messages")
    )
    
    # Get content type for Message model (for flagging)
    from django.contrib.contenttypes.models import ContentType
    message_content_type = ContentType.objects.get_for_model(Message)

    return render(request, "chat/conversation.html", {
        "conversation": conversation,
        "other_user": other_user,          # None for groups
        "messages": messages_qs,
        "all_conversations": all_conversations,
        "message_content_type_id": message_content_type.id,
    })

@login_required
def start_conversation(request):
    # ---------- POST: create DM or group ----------
    if request.method == "POST":
        selected_ids = request.POST.getlist("participants")
        group_name = (request.POST.get("group_name") or "").strip()

        if not selected_ids:
            messages.error(request, "Please select at least one user.")
            return redirect("chat:start_conversation")

        users = list(User.objects.filter(id__in=selected_ids))

        if len(users) == 1:
            # DM
            other = users[0]
            convo = Conversation.get_or_create_dm(request.user, other)
        else:
            # Group
            if not group_name:
                group_name = "Group chat"
            convo = Conversation.objects.create(
                name=group_name,
                is_group=True,
            )
            convo.participants.add(request.user, *users)

        return redirect("chat:conversation", convo_id=convo.id)

    # ---------- GET: show list of users to pick from ----------
    query = (request.GET.get('q') or '').strip()

    # All friends (so we know who is already a friend)
    friends_qs = Friend.get_friends(request.user).select_related('profile').order_by('username')
    friend_ids = list(friends_qs.values_list('id', flat=True))

    # Base queryset: by default, show just friends
    users_qs = friends_qs

    # Optional search: filter friends by display_name OR username OR email
    if query:
        users_qs = users_qs.filter(
            Q(profile__display_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(users_qs, 10)
    page_obj = paginator.get_page(page_number)

    role = getattr(getattr(request.user, 'profile', None), 'role', None)

    return render(request, 'chat/start_conversation.html', {
        'users': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'has_friends': friends_qs.exists(),
        'user_role': role,
        'friend_ids': friend_ids,
    })

@login_required
def create_group_conversation(request):
    if request.method == "POST":
        name = request.POST.get("name")
        user_ids = request.POST.getlist("participants")  # list of user IDs from form

        convo = Conversation.objects.create(
            name=name,
            is_group=True,
        )
        convo.participants.add(request.user)          # creator
        convo.participants.add(*User.objects.filter(id__in=user_ids))  # others

        return redirect("chat:conversation_detail", convo_id=convo.id)

    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat/create_group.html", {"users": users})

@login_required
def dm_with_user(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    convo = Conversation.get_or_create_dm(request.user, other_user)
    return redirect('chat:conversation', convo_id=convo.id)

@login_required
def find_friends(request):
    q = request.GET.get('q', '').strip()

    # current friends
    friend_ids = set(Friend.get_friends(request.user).values_list('id', flat=True))

    # outgoing pending (map to_user_id -> request id)
    outgoing = {
        fr.to_user_id: fr.id
        for fr in FriendRequest.objects
            .filter(from_user=request.user, status='pending')
            .only('id', 'to_user_id')
    }

    # incoming pending (from_user ids)
    incoming_ids = set(
        FriendRequest.objects
            .filter(to_user=request.user, status='pending')
            .values_list('from_user_id', flat=True)
    )

    # candidate users
    qs = User.objects.exclude(id=request.user.id)
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    qs = qs.order_by('username')[:50]

    users = []
    for u in qs:
        if u.id in friend_ids:
            status, cancel_req_id = 'friend', None
        elif u.id in outgoing:
            status, cancel_req_id = 'pending_sent', outgoing[u.id]   # <-- IMPORTANT
        elif u.id in incoming_ids:
            status, cancel_req_id = 'pending_received', None
        else:
            status, cancel_req_id = 'none', None
        users.append({'user': u, 'status': status, 'cancel_req_id': cancel_req_id})

    return render(request, 'chat/find_friends.html', {'users': users, 'query': q})


