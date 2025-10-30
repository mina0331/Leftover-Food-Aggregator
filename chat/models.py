from django.db import models
from django.contrib.auth.models import User
from profiles.models import Profile
from django.db.models import Q
# Create your models here.


class Friend(models.Model):
    pass

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
        sent_to - cls.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
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