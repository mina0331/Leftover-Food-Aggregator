from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import FlaggedContent, UserSuspension, ModeratorNotification, ModeratorActivityLog
from .forms import ModeratorPostEditForm, ModeratorMessageEditForm, SuspendUserForm, ReinstateUserForm
from posting.models import Post
from chat.models import Message
from userprivileges.roles import is_moderator
from profiles.models import Profile


def log_activity(organization, action_type, performed_by, description, related_content=None):
    """
    Helper function to create activity log entries
    """
    content_type = None
    object_id = None
    
    if related_content:
        content_type = ContentType.objects.get_for_model(related_content.__class__)
        object_id = related_content.id
    
    ModeratorActivityLog.objects.create(
        organization=organization,
        action_type=action_type,
        performed_by=performed_by,
        content_type=content_type,
        object_id=object_id,
        description=description
    )


@login_required
@require_POST
def flag_content(request):
    """
    Generic view to flag any content (Message, Post, etc.)
    Expects: content_type_id, object_id, reason
    """
    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')
    reason = request.POST.get('reason', '').strip()
    
    if not content_type_id or not object_id or not reason:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
        django_messages.error(request, "Please provide a reason for flagging.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        model_class = content_type.model_class()
        content_object = get_object_or_404(model_class, id=object_id)
        
        # Check if already flagged by this user
        existing_flag = FlaggedContent.objects.filter(
            content_type=content_type,
            object_id=object_id,
            flagged_by=request.user,
            status=FlaggedContent.Status.PENDING
        ).first()
        
        if existing_flag:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'You have already flagged this content'}, status=400)
            django_messages.info(request, "You have already flagged this content.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Create the flag
        flag = FlaggedContent.objects.create(
            content_type=content_type,
            object_id=object_id,
            flagged_by=request.user,
            reason=reason
        )
        
        # Log activity if content is from an organization
        if content_type.model == 'post' and hasattr(content_object, 'author'):
            author = content_object.author
            if hasattr(author, 'profile') and author.profile.role == Profile.Role.ORG:
                log_activity(
                    organization=author,
                    action_type=ModeratorActivityLog.ActionType.FLAG_CREATED,
                    performed_by=request.user,
                    description=f"Content flagged by {request.user.username}. Reason: {reason[:100]}",
                    related_content=flag
                )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Content flagged successfully. A moderator will review it.'})
        
        django_messages.success(request, "Content flagged successfully. A moderator will review it.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        django_messages.error(request, f"Error flagging content: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def review_flagged_content(request):
    """
    Moderator dashboard to review all flagged content
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to access this page.")
        return redirect('/')
    
    # Get search query
    search_query = request.GET.get('q', '').strip()
    
    # Get pending flags queryset (most recent first) - will paginate this
    pending_flags_qs = FlaggedContent.objects.filter(
        status=FlaggedContent.Status.PENDING
    ).select_related('flagged_by', 'content_type').prefetch_related('content_object').order_by('-flagged_at')
    
    # Apply search filter if query provided
    if search_query:
        # Search in reason, flagged_by username, and status
        search_q = Q(
            Q(reason__icontains=search_query) |
            Q(flagged_by__username__icontains=search_query) |
            Q(status__icontains=search_query)
        )
        
        # Also search in content text (for posts and messages)
        post_ct = ContentType.objects.get_for_model(Post)
        message_ct = ContentType.objects.get_for_model(Message)
        
        # Get post IDs that match search
        post_ids = Post.objects.filter(
            Q(event__icontains=search_query) |
            Q(event_description__icontains=search_query)
        ).values_list('id', flat=True)
        
        # Get message IDs that match search
        message_ids = Message.objects.filter(
            Q(content__icontains=search_query)
        ).values_list('id', flat=True)
        
        # Add content search to query
        search_q |= Q(
            Q(content_type=post_ct, object_id__in=post_ids) |
            Q(content_type=message_ct, object_id__in=message_ids)
        )
        
        pending_flags_qs = pending_flags_qs.filter(search_q)
    
    # Paginate pending flags (10 per page for better performance)
    paginator = Paginator(pending_flags_qs, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
        pending_flags_page = paginator.page(page_number)
    except (ValueError, TypeError):
        # Invalid page number, default to page 1
        pending_flags_page = paginator.page(1)
    except:
        # EmptyPage or other pagination errors, default to page 1
        pending_flags_page = paginator.page(1)
    
    # Get recently reviewed flags (limit to 20 for performance)
    reviewed_flags = FlaggedContent.objects.exclude(
        status=FlaggedContent.Status.PENDING
    ).select_related('flagged_by', 'reviewed_by', 'content_type').order_by('-reviewed_at')[:20]
    
    # Count by status (using efficient count queries)
    stats = {
        'pending': FlaggedContent.objects.filter(status=FlaggedContent.Status.PENDING).count(),
        'approved': FlaggedContent.objects.filter(status=FlaggedContent.Status.APPROVED).count(),
        'deleted': FlaggedContent.objects.filter(status=FlaggedContent.Status.DELETED).count(),
        'dismissed': FlaggedContent.objects.filter(status=FlaggedContent.Status.DISMISSED).count(),
        'edited': FlaggedContent.objects.filter(status=FlaggedContent.Status.EDITED).count(),
    }
    
    # Get violation counts for content authors (only for current page to optimize)
    violation_counts = {}
    post_ct = ContentType.objects.get_for_model(Post)
    message_ct = ContentType.objects.get_for_model(Message)
    
    # Get unique authors from current page of pending flags only
    authors = set()
    for flag in pending_flags_page:
        if flag.content_object:
            if flag.content_type.model == 'post':
                authors.add(flag.content_object.author)
            elif flag.content_type.model == 'message':
                authors.add(flag.content_object.sender)
    
    # Count violations per author (only for authors on current page)
    for author in authors:
        post_ids = Post.objects.filter(author=author).values_list('id', flat=True)
        message_ids = Message.objects.filter(sender=author).values_list('id', flat=True)
        
        count = FlaggedContent.objects.filter(
            Q(content_type=post_ct, object_id__in=post_ids) |
            Q(content_type=message_ct, object_id__in=message_ids)
        ).count()
        
        if count > 0:
            violation_counts[author.id] = {
                'user': author,
                'count': count,
                'is_suspended': author.profile.is_suspended() if hasattr(author, 'profile') else False
            }
    
    # Get unread notification count for current moderator
    unread_count = ModeratorNotification.objects.filter(
        moderator=request.user,
        is_read=False
    ).count()
    
    return render(request, 'moderation/review_flagged.html', {
        'pending_flags': pending_flags_page,
        'reviewed_flags': reviewed_flags,
        'stats': stats,
        'violation_counts': violation_counts,
        'search_query': search_query,
        'unread_notifications': unread_count,
    })


@login_required
@require_POST
def approve_flag(request, flag_id):
    """
    Approve flagged content (dismiss the flag - content is fine)
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    flag = get_object_or_404(FlaggedContent, id=flag_id)
    notes = request.POST.get('notes', '').strip()
    
    flag.approve(request.user, notes)
    django_messages.success(request, "Flag approved. Content remains visible.")
    
    return redirect('moderation:review_flagged')


@login_required
@require_POST
def dismiss_flag(request, flag_id):
    """
    Dismiss the flag (content is fine, no action needed)
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    flag = get_object_or_404(FlaggedContent, id=flag_id)
    notes = request.POST.get('notes', '').strip()
    
    flag.dismiss(request.user, notes)
    django_messages.success(request, "Flag dismissed.")
    
    return redirect('moderation:review_flagged')


@login_required
@require_POST
def delete_flagged_content(request, flag_id):
    """
    Delete the flagged content
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    flag = get_object_or_404(FlaggedContent, id=flag_id)
    notes = request.POST.get('notes', '').strip()
    
    # Get organization before deleting
    organization = None
    if flag.content_object:
        if flag.content_type.model == 'post':
            organization = flag.content_object.author
        elif flag.content_type.model == 'message':
            organization = flag.content_object.sender
    
    flag.delete_content(request.user, notes)
    
    # Log activity if organization exists
    if organization and hasattr(organization, 'profile') and organization.profile.role == Profile.Role.ORG:
        log_activity(
            organization=organization,
            action_type=ModeratorActivityLog.ActionType.CONTENT_DELETED,
            performed_by=request.user,
            description=f"Content deleted by moderator {request.user.username}. Notes: {notes[:100] if notes else 'No notes'}",
            related_content=flag
        )
    
    django_messages.success(request, "Flagged content has been deleted.")
    
    return redirect('moderation:review_flagged')


@login_required
def edit_flagged_content(request, flag_id):
    """
    Edit flagged content (Post or Message)
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    flag = get_object_or_404(FlaggedContent, id=flag_id)
    
    # Check if content still exists
    if not flag.content_object:
        django_messages.error(request, "Content has been deleted and cannot be edited.")
        return redirect('moderation:review_flagged')
    
    content_object = flag.content_object
    content_type = flag.content_type
    
    # Determine content type and get appropriate form
    if content_type.model == 'post':
        model_class = Post
        form_class = ModeratorPostEditForm
    elif content_type.model == 'message':
        model_class = Message
        form_class = ModeratorMessageEditForm
    else:
        django_messages.error(request, "This content type cannot be edited.")
        return redirect('moderation:review_flagged')
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=content_object)
        notes = request.POST.get('moderator_notes', '').strip()
        
        if form.is_valid():
            # Handle image removal for posts
            if content_type.model == 'post' and 'remove_image' in request.POST:
                if content_object.image:
                    content_object.image.delete(save=False)
                    content_object.image = None
            
            form.save()
            
            # Mark flag as edited
            flag.edit_content(request.user, notes)
            
            # Log activity if organization exists
            organization = None
            if content_type.model == 'post':
                organization = content_object.author
            elif content_type.model == 'message':
                organization = content_object.sender
            
            if organization and hasattr(organization, 'profile') and organization.profile.role == Profile.Role.ORG:
                log_activity(
                    organization=organization,
                    action_type=ModeratorActivityLog.ActionType.CONTENT_EDITED,
                    performed_by=request.user,
                    description=f"Content edited by moderator {request.user.username}. Notes: {notes[:100] if notes else 'No notes'}",
                    related_content=content_object
                )
            
            django_messages.success(request, "Content has been edited successfully.")
            return redirect('moderation:review_flagged')
        else:
            django_messages.error(request, "Please fix the errors in the form.")
    else:
        form = form_class(instance=content_object)
    
    return render(request, 'moderation/edit_content.html', {
        'flag': flag,
        'form': form,
        'content_object': content_object,
        'content_type_name': flag.get_content_type_name(),
    })


@login_required
def suspend_user(request, user_id):
    """
    Suspend a user for violations
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    user_to_suspend = get_object_or_404(User, id=user_id)
    
    # Prevent suspending moderators/staff
    if user_to_suspend.is_staff or user_to_suspend.is_superuser or is_moderator(user_to_suspend):
        django_messages.error(request, "Cannot suspend moderators or staff members.")
        return redirect('moderation:manage_suspensions')
    
    # Check if user already has active suspension
    active_suspension = UserSuspension.objects.filter(
        user=user_to_suspend,
        is_active=True
    ).first()
    
    if active_suspension and not active_suspension.is_expired():
        django_messages.warning(request, f"{user_to_suspend.username} is already suspended.")
        return redirect('moderation:user_suspension_history', user_id=user_to_suspend.id)
    
    if request.method == 'POST':
        form = SuspendUserForm(request.POST)
        if form.is_valid():
            suspension = UserSuspension.objects.create(
                user=user_to_suspend,
                suspended_by=request.user,
                reason=form.cleaned_data['reason'],
                suspended_until=form.cleaned_data.get('suspended_until')
            )
            
            # Log activity if suspended user is an organization
            if hasattr(user_to_suspend, 'profile') and user_to_suspend.profile.role == Profile.Role.ORG:
                log_activity(
                    organization=user_to_suspend,
                    action_type=ModeratorActivityLog.ActionType.USER_SUSPENDED,
                    performed_by=request.user,
                    description=f"User suspended by moderator {request.user.username}. Reason: {form.cleaned_data['reason'][:100]}",
                    related_content=suspension
                )
            
            django_messages.success(
                request,
                f"{user_to_suspend.username} has been suspended. {suspension.get_duration_display()}."
            )
            return redirect('moderation:manage_suspensions')
    else:
        form = SuspendUserForm()
    
    # Get user's violation count (more efficient query)
    post_ids = Post.objects.filter(author=user_to_suspend).values_list('id', flat=True)
    message_ids = Message.objects.filter(sender=user_to_suspend).values_list('id', flat=True)
    
    post_ct = ContentType.objects.get_for_model(Post)
    message_ct = ContentType.objects.get_for_model(Message)
    
    violation_count = FlaggedContent.objects.filter(
        Q(content_type=post_ct, object_id__in=post_ids) |
        Q(content_type=message_ct, object_id__in=message_ids)
    ).count()
    
    return render(request, 'moderation/suspend_user.html', {
        'user_to_suspend': user_to_suspend,
        'form': form,
        'violation_count': violation_count,
        'active_suspension': active_suspension,
    })


@login_required
@require_POST
def reinstate_user(request, suspension_id):
    """
    Reinstate a suspended user
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to perform this action.")
        return redirect('/')
    
    suspension = get_object_or_404(UserSuspension, id=suspension_id)
    
    if not suspension.is_active:
        django_messages.info(request, "This suspension has already been reinstated.")
        return redirect('moderation:manage_suspensions')
    
    form = ReinstateUserForm(request.POST)
    if form.is_valid():
        notes = form.cleaned_data.get('notes', '')
        suspension.reinstate(request.user, notes)
        
        # Log activity if reinstated user is an organization
        if hasattr(suspension.user, 'profile') and suspension.user.profile.role == Profile.Role.ORG:
            log_activity(
                organization=suspension.user,
                action_type=ModeratorActivityLog.ActionType.USER_REINSTATED,
                performed_by=request.user,
                description=f"User reinstated by moderator {request.user.username}. Notes: {notes[:100] if notes else 'No notes'}",
                related_content=suspension
            )
        
        django_messages.success(request, f"{suspension.user.username} has been reinstated.")
        return redirect('moderation:manage_suspensions')
    
    django_messages.error(request, "Error reinstating user.")
    return redirect('moderation:manage_suspensions')


@login_required
def manage_suspensions(request):
    """
    Moderator dashboard for managing all suspensions
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to access this page.")
        return redirect('/')
    
    # Handle user search
    search_query = request.GET.get('q', '').strip()
    search_results = None
    
    if search_query:
        # Search for users by username or email (exclude moderators/staff)
        from profiles.models import Profile
        search_users = User.objects.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        ).exclude(
            is_staff=True
        ).exclude(
            is_superuser=True
        ).exclude(
            profile__role=Profile.Role.MODERATOR
        ).select_related('profile').order_by('username')[:50]
        
        # Get violation counts and suspension status for each user
        post_ct = ContentType.objects.get_for_model(Post)
        message_ct = ContentType.objects.get_for_model(Message)
        
        search_results = []
        for user in search_users:
            # Get violation count
            post_ids = Post.objects.filter(author=user).values_list('id', flat=True)
            message_ids = Message.objects.filter(sender=user).values_list('id', flat=True)
            
            violation_count = FlaggedContent.objects.filter(
                Q(content_type=post_ct, object_id__in=post_ids) |
                Q(content_type=message_ct, object_id__in=message_ids)
            ).count()
            
            # Get active suspension
            active_suspension = UserSuspension.objects.filter(
                user=user,
                is_active=True
            ).first()
            
            if active_suspension and active_suspension.is_expired():
                active_suspension.is_active = False
                active_suspension.save()
                active_suspension = None
            
            search_results.append({
                'user': user,
                'violation_count': violation_count,
                'active_suspension': active_suspension,
                'is_suspended': active_suspension is not None and not active_suspension.is_expired(),
            })
    
    # Get active suspensions
    active_suspensions = UserSuspension.objects.filter(is_active=True).select_related(
        'user', 'suspended_by'
    ).order_by('-suspended_at')
    
    # Check for expired suspensions and auto-reinstate
    for suspension in active_suspensions:
        if suspension.is_expired():
            suspension.is_active = False
            suspension.save()
    
    # Refresh active suspensions after auto-reinstatement
    active_suspensions = UserSuspension.objects.filter(is_active=True).select_related(
        'user', 'suspended_by'
    ).order_by('-suspended_at')
    
    # Get recently reinstated
    reinstated_suspensions = UserSuspension.objects.filter(
        is_active=False
    ).select_related('user', 'suspended_by', 'reinstated_by').order_by('-reinstated_at')[:20]
    
    # Stats
    stats = {
        'active': active_suspensions.count(),
        'reinstated': UserSuspension.objects.filter(is_active=False).count(),
        'permanent': UserSuspension.objects.filter(is_active=True, suspended_until__isnull=True).count(),
        'temporary': UserSuspension.objects.filter(is_active=True, suspended_until__isnull=False).count(),
    }
    
    return render(request, 'moderation/manage_suspensions.html', {
        'active_suspensions': active_suspensions,
        'reinstated_suspensions': reinstated_suspensions,
        'stats': stats,
        'search_query': search_query,
        'search_results': search_results,
    })


@login_required
def user_suspension_history(request, user_id):
    """
    View a user's suspension history
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to access this page.")
        return redirect('/')
    
    user = get_object_or_404(User, id=user_id)
    suspensions = UserSuspension.objects.filter(user=user).select_related(
        'suspended_by', 'reinstated_by'
    ).order_by('-suspended_at')
    
    # Get violation count (more efficient query)
    post_ids = Post.objects.filter(author=user).values_list('id', flat=True)
    message_ids = Message.objects.filter(sender=user).values_list('id', flat=True)
    
    post_ct = ContentType.objects.get_for_model(Post)
    message_ct = ContentType.objects.get_for_model(Message)
    
    violation_count = FlaggedContent.objects.filter(
        Q(content_type=post_ct, object_id__in=post_ids) |
        Q(content_type=message_ct, object_id__in=message_ids)
    ).count()
    
    active_suspension = suspensions.filter(is_active=True).first()
    if active_suspension and active_suspension.is_expired():
        active_suspension.is_active = False
        active_suspension.save()
        active_suspension = None
    
    return render(request, 'moderation/user_suspension_history.html', {
        'user': user,
        'suspensions': suspensions,
        'active_suspension': active_suspension,
        'violation_count': violation_count,
    })


@login_required
def suspension_notice(request, suspension_id):
    """
    Show suspension notice to suspended users
    """
    suspension = get_object_or_404(UserSuspension, id=suspension_id)
    
    # Verify this suspension belongs to the current user
    if suspension.user != request.user:
        django_messages.error(request, "You don't have permission to view this page.")
        return redirect('/')
    
    # Check if suspension is still active
    if not suspension.is_active or suspension.is_expired():
        if suspension.is_expired():
            suspension.is_active = False
            suspension.save()
        django_messages.info(request, "Your suspension has expired. You can now access the site.")
        return redirect('/')
    
    return render(request, 'moderation/suspension_notice.html', {
        'suspension': suspension,
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    notification = get_object_or_404(ModeratorNotification, id=notification_id, moderator=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('moderation:review_flagged')


@login_required
def organization_activity_log(request, user_id=None):
    """
    View activity log for a specific organization
    """
    if not (is_moderator(request.user) or request.user.is_staff or request.user.is_superuser):
        django_messages.error(request, "You don't have permission to access this page.")
        return redirect('/')
    
    from profiles.models import Profile
    
    # Get organization from user_id or username
    organization = None
    if user_id:
        organization = get_object_or_404(User, id=user_id)
    else:
        username = request.GET.get('username', '').strip()
        if username:
            try:
                organization = User.objects.get(username=username)
            except User.DoesNotExist:
                django_messages.error(request, f"Organization '{username}' not found.")
                return redirect('moderation:review_flagged')
    
    if not organization:
        django_messages.error(request, "Please specify an organization.")
        return redirect('moderation:review_flagged')
    
    # Verify it's an organization
    if not hasattr(organization, 'profile') or organization.profile.role != Profile.Role.ORG:
        django_messages.error(request, f"{organization.username} is not an organization.")
        return redirect('moderation:review_flagged')
    
    # Get activity logs for this organization
    activity_logs = ModeratorActivityLog.objects.filter(
        organization=organization
    ).select_related('performed_by', 'content_type').order_by('-created_at')
    
    # Paginate
    paginator = Paginator(activity_logs, 20)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
        activity_logs_page = paginator.page(page_number)
    except (ValueError, TypeError):
        activity_logs_page = paginator.page(1)
    except:
        activity_logs_page = paginator.page(1)
    
    return render(request, 'moderation/organization_activity_log.html', {
        'organization': organization,
        'activity_logs': activity_logs_page,
    })
