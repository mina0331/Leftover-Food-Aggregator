from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from django.db.models import Q
from django.db.models import Count
from Friendslist.models import Friend, FriendRequest
from datetime import datetime
# Create your models here.

class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True)  # for group name
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_group and self.name:
            return self.name
        return f"Conversation {self.id}"

    @classmethod
    def get_or_create_dm(cls, user1, user2):
        from django.db.models import Count

        qs = cls.objects.filter(
            is_group=False,
            participants=user1,
        ).annotate(num_participants=Count('participants')).filter(
            num_participants=2,
            participants__in=[user2],
        )

        convo = qs.first()
        if convo:
            return convo

        convo = cls.objects.create(is_group=False)
        convo.participants.add(user1, user2)
        return convo

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_messages",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:30]}"

    @classmethod
    def get_conversations(cls, user):
        # 1) Who have I chatted with?
        sent_to = cls.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
        received_from = cls.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
        user_ids = set(sent_to).union(set(received_from))
        if not user_ids:
            return []

        # 2) Load all “other” users in bulk (avoid N+1)
        others = User.objects.in_bulk(user_ids)  # dict {id: User}

        conversations = []
        for oid, other_user in others.items():
            # 3) Latest message between us
            last_msg = (
                cls.objects
                .filter(
                    Q(sender=user, recipient=other_user) |
                    Q(sender=other_user, recipient=user)
                )
                .only('content', 'timestamp')  # small optimization
                .order_by('-timestamp')
                .first()
            )

            # 4) Unread messages from the other user → me
            unread_count = cls.objects.filter(
                sender=other_user,
                recipient=user,
                is_read=False
            ).count()

            conversations.append({
                'other_user': other_user,
                'last_message': last_msg.content if last_msg else '',
                'last_message_time': last_msg.timestamp if last_msg else None,
                'unread_count': unread_count,
            })

        # 5) Sort most-recent first (None goes last)
        conversations.sort(
            key=lambda c: c['last_message_time'] or datetime.min,
            reverse=True
        )
        return conversations

    @classmethod
    def send_request(cls, from_user, to_user):
        """Send a friend request if it doesn’t already exist."""
        if from_user == to_user:
            return None  # cannot friend yourself
        # check if any existing pending or accepted request between the pair
        existing = cls.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user),
            status__in=['pending', 'accepted']
        ).first()
        if existing:
            return existing
        return cls.objects.create(from_user=from_user, to_user=to_user, status='pending')

    def accept(self):
        """Accept the friend request and add to both users’ friend lists."""
        from .models import Friend  # import here to avoid circular imports
        self.status = 'accepted'
        self.save()
        Friend.make_friends(self.from_user, self.to_user)
        return self

    def reject(self):
        """Reject the friend request."""
        self.status = 'rejected'
        self.save()
        return self


