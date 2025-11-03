# chat/models.py
from django.db import models, transaction
from django.db.models import Q, F
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Friend(models.Model):
    # Store each friendship once with (user1_id < user2_id)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_edges_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_edges_as_user2')

    class Meta:
        unique_together = (('user1', 'user2'),)
        constraints = [
            models.CheckConstraint(check=Q(user1__lt=F('user2')), name='friend_user1_lt_user2'),
        ]

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"

    @classmethod
    def normalize_pair(cls, a: User, b: User):
        return (a, b) if a.id < b.id else (b, a)

    @classmethod
    def make_friends(cls, a: User, b: User):
        if a.id == b.id:
            return  # or raise ValueError("Cannot friend yourself")
        u1, u2 = cls.normalize_pair(a, b)
        cls.objects.get_or_create(user1=u1, user2=u2)

    @classmethod
    def break_friends(cls, a: User, b: User):
        u1, u2 = cls.normalize_pair(a, b)
        cls.objects.filter(user1=u1, user2=u2).delete()

    @classmethod
    def are_friends(cls, a: User, b: User) -> bool:
        u1, u2 = cls.normalize_pair(a, b)
        return cls.objects.filter(user1=u1, user2=u2).exists()

    @classmethod
    def get_friends(cls, user: User):
        return User.objects.filter(
            Q(friend_edges_as_user1__user2=user) |  # entries where other is user2 and user is user1
            Q(friend_edges_as_user2__user1=user)    # entries where other is user1 and user is user2
        ).distinct()

    def other_user(self, me: User) -> User:
        return self.user2 if self.user1_id == me.id else self.user1


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user   = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('from_user', 'to_user')
        indexes = [models.Index(fields=['from_user', 'to_user'])]

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"
