from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Friend, FriendRequest

@login_required
def FriendsList_index(request):
    friends = (Friend.get_friends(request.user)
               .select_related('profile')
               .order_by('username'))

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
        return redirect(request.META.get('HTTP_REFERER') or 'friends:friends_list')

    fr = get_object_or_404(
        FriendRequest,
        id=req_id,
        to_user=request.user,
        status='pending'
    )

    with transaction.atomic():
        Friend.make_friends(fr.from_user, fr.to_user)
        fr.status = 'accepted'
        fr.save(update_fields=['status'])

    messages.success(request, f"You and {fr.from_user.username} are now friends.")
    return redirect('friends:friends_list')


@login_required
def reject_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')                 # <-- fixed namespace

    fr = get_object_or_404(FriendRequest, id=req_id, to_user=request.user, status='pending')
    fr.status = 'rejected'                                     # <-- don't call fr.reject()
    fr.save(update_fields=['status'])
    messages.info(request, f"Request from {fr.from_user.username} rejected.")
    return redirect('friends:friends_list')                    # <-- fixed namespace


@login_required
def cancel_friend_request(request, req_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')                # <-- fixed namespace

    fr = get_object_or_404(FriendRequest, id=req_id, from_user=request.user, status='pending')
    fr.delete()
    messages.info(request, "Friend request canceled.")
    return redirect('friends:friends_list')                    # <-- fixed namespace


@login_required
def remove_friend(request, user_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')                # <-- fixed namespace

    other = get_object_or_404(User, id=user_id)
    Friend.break_friends(request.user, other)
    messages.warning(request, f"Removed {other.username} from your friends.")
    return redirect('friends:friends_list')                    # <-- fixed namespace


@login_required
def send_friend_request(request, user_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')

    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "You can’t add yourself.")
        return redirect('friends:friends_list')

    if Friend.get_friends(request.user).filter(id=to_user.id).exists():
        messages.info(request, "You’re already friends.")
        return redirect('friends:friends_list')

    pending_exists = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user),
        status='pending'
    ).exists()
    if pending_exists:
        messages.info(request, "A request is already pending.")
        return redirect('friends:friends_list')

    FriendRequest.objects.create(from_user=request.user, to_user=to_user, status='pending')
    messages.success(request, f"Friend request sent to {to_user.username}.")
    return redirect('friends:friends_list')
