"""
Django management command to list all organizations with their IDs
for easy access to activity logs
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import Profile


class Command(BaseCommand):
    help = 'List all organizations with their user IDs for activity log access'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Organizations ===\n'))
        
        org_users = User.objects.filter(profile__role=Profile.Role.ORG).select_related('profile')
        
        if not org_users.exists():
            self.stdout.write(self.style.WARNING('No organizations found.'))
            return
        
        self.stdout.write(f"{'Username':<30} {'User ID':<10} {'Email':<30} {'Activity Log URL'}")
        self.stdout.write('-' * 100)
        
        for user in org_users:
            activity_log_url = f'/moderation/activity-log/{user.id}/'
            self.stdout.write(
                f"{user.username:<30} {user.id:<10} {user.email or 'N/A':<30} {activity_log_url}"
            )
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(
            'To view activity log, visit: http://127.0.0.1:8000/moderation/activity-log/<user_id>/'
        ))
        self.stdout.write('\n')

