from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message


# Create your views here.
@login_required
def messages_index(request):
    conversations = Message.get_conversations(request.user)

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

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            return redirect('chat:conversations', user_id=user_id)
    return render(request, 'chat/conversation.html', {
        'users' : users,
        'query' : query
    })
