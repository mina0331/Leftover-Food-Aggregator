from django.core.management.base import BaseCommand
from django.utils import timezone
from posting.models import Post


class Command(BaseCommand):
    help = 'Publishes all scheduled posts whose publish_at time has passed'

    def handle(self, *args, **options):
        # Find all scheduled posts where publish_at <= current time
        now = timezone.now()
        scheduled_posts = Post.objects.filter(
            status=Post.Status.SCHEDULED,
            publish_at__lte=now
        )

        # Count how many posts we're about to publish
        count = scheduled_posts.count()

        # Update their status to PUBLISHED
        scheduled_posts.update(status=Post.Status.PUBLISHED)

        # Print success message
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No scheduled posts to publish.'))
        elif count == 1:
            self.stdout.write(self.style.SUCCESS('Successfully published 1 post.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully published {count} posts.'))

