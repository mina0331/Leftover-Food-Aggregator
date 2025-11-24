from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Friend, FriendRequest

@login_required
def FriendsList_index(request):
    user = request.user

    friends = (
        Friend.get_friends(user)
        .select_related('profile')
        .order_by('username')
    )

    received_reqs = (
        FriendRequest.objects
        .filter(to_user=user, status='pending')
        .select_related('from_user__profile')
        .order_by('-created_at')
    )

    sent_reqs = (
        FriendRequest.objects
        .filter(from_user=user, status='pending')
        .select_related('to_user__profile')
        .order_by('-created_at')
    )

    # --- NEW: search for non-friends ---
    search_query = request.GET.get("search", "").strip()
    search_results = []

    if search_query:
        # IDs you should NOT show in results
        exclude_ids = {user.id}
        exclude_ids.update(friends.values_list("id", flat=True))
        exclude_ids.update(received_reqs.values_list("from_user_id", flat=True))
        exclude_ids.update(sent_reqs.values_list("to_user_id", flat=True))

        search_results = (
            User.objects
            .filter(
                Q(profile__display_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            .exclude(id__in=exclude_ids)
            .select_related("profile")
            .order_by("username")[:20]
        )
    # -----------------------------------

    return render(request, 'Friendslist/index.html', {
        'friends': friends,
        'received_reqs': received_reqs,
        'sent_reqs': sent_reqs,
        'counts': {
            'friends': friends.count(),
            'received': received_reqs.count(),
            'sent': sent_reqs.count(),
        },
        'search_query': search_query,
        'search_results': search_results,
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
    return redirect('friends:friends_list')


@login_required
def remove_friend(request, user_id):
    if request.method != 'POST':
        return redirect('friends:friends_list')

    other = get_object_or_404(User, id=user_id)

    # 1) Remove friendship
    Friend.break_friends(request.user, other)

    # 2) Remove any friend requests between these two (both directions)
    FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=other) |
        Q(from_user=other, to_user=request.user)
    ).delete()

    messages.warning(request, f"Removed {other.username} from your friends.")

    return redirect('friends:friends_list')

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect('view_profile', user_id=user_id)


    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={"status": "pending"},
    )

    if created:
        messages.success(request, "Friend request sent!")
    else:
        # row already exists — decide what you want:
        # you can either show a message:
        messages.info(request, "You already sent a friend request to this user.")


    return redirect('profiles:view_profile', user_id=user_id)