from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from django.db.models import Q
# Create your models here.


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_with')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} & {self.friend.username}"

    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            Q(user=user1, friend=user2) | Q(user=user2, friend=user1)
        ).exists()

    @classmethod
    def get_friends(cls, user):
        """Get all friends for a user"""
        # Get friends where user is either the 'user' or 'friend' in the relationship
        friend_ids_1 = cls.objects.filter(user=user).values_list('friend', flat=True)
        friend_ids_2 = cls.objects.filter(friend=user).values_list('user', flat=True)

        all_friend_ids = set(list(friend_ids_1) + list(friend_ids_2))
        return User.objects.filter(id__in=all_friend_ids)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:30]}"

    @classmethod
    def get_conversation(cls, user):
        sent_to = cls.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
        received_from = cls.objects.filter(recipient=user).values_list('sender', flat=True).distinct()

        user_ids = set(list(sent_to) + list(received_from))

        conversations = []
        for user_id in user_ids:
            other_user = User.objects.get(id=user_id)
            last_message = cls.objects.filter(Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)).order_by('-timestamp').first()

            unread_count = cls.objects.filter(sender=other_user, recipient=user, is_read=False).count()
            conversations.append({'other_user': other_user,
                                  'last_message': last_message.content if last_message else '',
                                  last_message.time: last_message.timestamp if last_message else None,
                                  unread_count: unread_count
                                  })
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        return conversations