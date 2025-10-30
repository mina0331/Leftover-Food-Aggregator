from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Case, When, IntegerField
from .models import Message
from .models import Friend
from .models import FriendRequest


# Create your views here.
@login_required
def messages_index(request):
    conversations = Message.get_conversation(request.user)

    return render(request, 'chat/index.html', {'conversations': conversations})

@login_required
def conversation_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    Message.objects.filter(
        sender = other_user,
        recipient = request.user,
        is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            Message.objects.create(
                sender = request.user,
                recipient = other_user,
                content = content
            )
            return redirect('chat:conversations', user_id=user_id)

    all_conversations = Message.get_conversations(request.user)

    return render(request, 'chat/conversation.html',
                  {'other_user': other_user,
                'messages' : messages,
                'all_conversations' : all_conversations})


@login_required
def start_conversation(request):
    users = []
    query = request.GET.get('q', '').strip()

    # Get all friends of current user
    friends = Friend.get_friends(request.user)

    if query:
        # Search only within friends
        users = friends.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )[:10]
    else:
        # Show all friends if no query
        users = friends
    profile = getattr(request.user, 'profile', None)
    user_role = getattr(profile, 'role', None)

    return render(request, 'chat/start_conversation.html', {
        'users': users,
        'query': query,
        'has_friends': friends.exists(),
        'user_role' : user_role,
    })

@login_required
def find_friends(request):
    q = request.GET.get('q', '').strip()

    # Current friends (assumes Friend.get_friends(user) -> queryset of Users)
    friend_qs = Friend.get_friends(request.user)
    friend_ids = set(friend_qs.values_list('id', flat=True))

    # Pending requests (adapt model/field names if yours differ)
    # Assumes a FriendRequest model with from_user, to_user, status='pending'
    pending_sent_ids = set(
        FriendRequest.objects.filter(from_user=request.user, status='pending')
        .values_list('to_user_id', flat=True)
    )
    pending_received_ids = set(
        FriendRequest.objects.filter(to_user=request.user, status='pending')
        .values_list('from_user_id', flat=True)
    )

    # Base pool: all non-self, non-friends
    pool = (User.objects
            .select_related('profile')
            .exclude(id=request.user.id)
            .exclude(id__in=friend_ids))

    users_qs = pool
    if q:
        users_qs = users_qs.filter(Q(username__icontains=q) | Q(email__icontains=q)).annotate(
            priority=Case(
                When(Q(username__iexact=q) | Q(email__iexact=q), then=0),
                When(Q(username__istartswith=q) | Q(email__istartswith=q), then=1),
                default=2,
                output_field=IntegerField()
            )
        ).order_by('priority', 'username')
    else:
        users_qs = users_qs.order_by('username')

    # Build the structure your template expects
    users = []
    for u in users_qs[:50]:
        if u.id in friend_ids:
            status = 'friend'
        elif u.id in pending_sent_ids:
            status = 'pending_sent'
        elif u.id in pending_received_ids:
            status = 'pending_received'
        else:
            status = 'none'
        users.append({'user': u, 'status': status})

    # pass role if needed
    profile = getattr(request.user, 'profile', None)
    user_role = getattr(profile, 'role', None)

    return render(request, 'chat/find_friends.html', {
        'users': users,
        'query': q,
        'user_role': user_role,
    })

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
