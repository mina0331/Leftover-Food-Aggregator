from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import FlaggedContent
from userprivileges.roles import is_moderator


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
    
    # Get pending flags (most recent first)
    pending_flags = FlaggedContent.objects.filter(
        status=FlaggedContent.Status.PENDING
    ).select_related('flagged_by', 'content_type').prefetch_related('content_object')
    
    # Get recently reviewed flags
    reviewed_flags = FlaggedContent.objects.exclude(
        status=FlaggedContent.Status.PENDING
    ).select_related('flagged_by', 'reviewed_by', 'content_type').order_by('-reviewed_at')[:20]
    
    # Count by status
    stats = {
        'pending': FlaggedContent.objects.filter(status=FlaggedContent.Status.PENDING).count(),
        'approved': FlaggedContent.objects.filter(status=FlaggedContent.Status.APPROVED).count(),
        'deleted': FlaggedContent.objects.filter(status=FlaggedContent.Status.DELETED).count(),
        'dismissed': FlaggedContent.objects.filter(status=FlaggedContent.Status.DISMISSED).count(),
    }
    
    return render(request, 'moderation/review_flagged.html', {
        'pending_flags': pending_flags,
        'reviewed_flags': reviewed_flags,
        'stats': stats,
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
    
    flag.delete_content(request.user, notes)
    django_messages.success(request, "Flagged content has been deleted.")
    
    return redirect('moderation:review_flagged')
