from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Case, When, IntegerField
from .models import Message
from .models import Friend
from .models import FriendRequest
from django.contrib import messages
from django.core.paginator import Paginator


# Create your views here.
@login_required
def messages_index(request):
    conversations = Message.get_conversations(request.user)

    return render(request, 'chat/index.html', {'conversations': conversations})

@login_required
def conversation_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # fetch the thread
    thread_qs = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')

    # mark incoming as read
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    # send a new message
    if request.method == 'POST':
        content = (request.POST.get('message') or '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
        return redirect('chat:conversation', user_id=other_user.id)

    # sidebar list (if you have this helper)
    all_conversations = Message.get_conversations(request.user)

    return render(request, 'chat/conversation.html', {
        'other_user': other_user,
        'messages': thread_qs,
        'all_conversations': all_conversations,
    })

@login_required
def start_conversation(request):
    query = (request.GET.get('q') or '').strip()

    # 1) Base queryset: all friends as Users
    friends_qs = Friend.get_friends(request.user).select_related('profile').order_by('username')

    # 2) Optional search inside friends
    if query:
        friends_qs = friends_qs.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # 3) Pagination (10 per page by default)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(friends_qs, 10)
    page_obj = paginator.get_page(page_number)

    # 4) Role (defensive)
    role = getattr(getattr(request.user, 'profile', None), 'role', None)

    return render(request, 'chat/start_conversation.html', {
        'users': page_obj.object_list,   # iterate as usual
        'page_obj': page_obj,            # for next/prev links
        'query': query,
        'has_friends': friends_qs.exists(),
        'user_role': role,
    })
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

@login_required
def send_friend_request(request, user_id):
    if request.method != 'POST':
        return redirect('chat:find_friends')

    to_user = get_object_or_404(User, id=user_id)
    if to_user == request.user:
        messages.error(request, "You can’t add yourself.")
        return redirect('chat:find_friends')

    # already friends?
    if Friend.get_friends(request.user).filter(id=to_user.id).exists():
        messages.info(request, "You’re already friends.")
        return redirect('chat:find_friends')

    # already pending either direction?
    exists = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user),
        status='pending'
    ).exists()
    if exists:
        messages.info(request, "A request is already pending.")
        return redirect('chat:find_friends')

    FriendRequest.objects.create(from_user=request.user, to_user=to_user, status='pending')
    messages.success(request, "Friend request sent.")
    return redirect('chat:find_friends')

@login_required
def cancel_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')

    fr = get_object_or_404(
        FriendRequest,
        id=req_id,
        from_user=request.user,   # only the sender can cancel their own pending request
        status='pending'
    )
    fr.delete()
    messages.info(request, "Friend request canceled.")
    return redirect('friends:friends_list')

