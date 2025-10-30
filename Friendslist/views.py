from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from chat.models import Friend, FriendRequest
# Create your views here.
@login_required
def FriendsList_index(request):

    friends = (Friend.get_friends(request.user)
               .select_related('profile')
               .order_by('username'))

    # Pending requests
    received_reqs = (FriendRequest.objects
                     .filter(to_user=request.user, status='pending')
                     .select_related('from_user__profile')
                     .order_by('-created_at'))

    sent_reqs = (FriendRequest.objects
                 .filter(from_user=request.user, status='pending')
                 .select_related('to_user__profile')
                 .order_by('-created_at'))

    return render(request, 'Friendslist/index.html', {
        'friends': friends,
        'received_reqs': received_reqs,
        'sent_reqs': sent_reqs,
        'counts': {
            'friends': friends.count(),
            'received': received_reqs.count(),
            'sent': sent_reqs.count(),
        }
    })

@login_required
def accept_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('chat:friends_list')

    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status='pending')
    fr.accept()  # will mark accepted + create friendship
    messages.success(request, f"You and {fr.from_user.username} are now friends.")
    return redirect('chat:friends_list')


@login_required
def reject_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('chat:friends_list')

    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status='pending')
    fr.reject()
    messages.info(request, f"Request from {fr.from_user.username} rejected.")
    return redirect('chat:friends_list')


@login_required
def cancel_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('chat:friends_list')

    fr = get_object_or_404(FriendRequest, id=req_id, from_user=request.user, status='pending')
    fr.delete()
    messages.info(request, "Friend request canceled.")
    return redirect('chat:friends_list')


@login_required
def remove_friend(request, user_id):
    if request.method != 'POST':
        return redirect('chat:friends_list')

    other = get_object_or_404(User, id=user_id)
    # implement your Friend model’s remove/break helper as needed:
    Friend.break_friends(request.user, other)  # <- write this in your Friend model
    messages.warning(request, f"Removed {other.username} from your friends.")
    return redirect('chat:friends_list')

@login_required
def send_friend_request(request, user_id):
    if request.method != 'POST':
        # Don’t allow GET to create requests; just go back to friends hub
        return redirect('friends:friends_list')

    to_user = get_object_or_404(User, id=user_id)

    # 1) no self-requests
    if to_user == request.user:
        messages.error(request, "You can’t add yourself.")
        return redirect('friends:friends_list')

    # 2) already friends?
    if Friend.get_friends(request.user).filter(id=to_user.id).exists():
        messages.info(request, "You’re already friends.")
        return redirect('friends:friends_list')

    # 3) any pending request either direction?
    pending_exists = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user),
        status='pending'
    ).exists()
    if pending_exists:
        messages.info(request, "A request is already pending.")
        return redirect('friends:friends_list')

    # 4) create the pending request
    FriendRequest.objects.create(from_user=request.user, to_user=to_user, status='pending')
    messages.success(request, f"Friend request sent to {to_user.username}.")
    return redirect('friends:friends_list')

@login_required
def cancel_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')

    fr = get_object_or_404(FriendRequest, id=req_id, from_user=request.user, status='pending')
    fr.delete()
    messages.info(request, "Friend request canceled.")
    return redirect('friends:friends_list')