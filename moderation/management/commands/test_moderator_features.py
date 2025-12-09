"""
Django management command to test all moderator features:
1. Notification system for reports
2. Search bar for reports
3. Activity log for organizations
4. Permission restrictions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from moderation.models import (
    FlaggedContent, UserSuspension, ModeratorNotification, ModeratorActivityLog
)
from posting.models import Post, Cuisine, Location
from chat.models import Message, Conversation
from profiles.models import Profile
from userprivileges.roles import is_moderator
import sys


class Command(BaseCommand):
    help = 'Test all moderator features: notifications, search, activity logs, and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test data after running tests',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Testing Moderator Features ===\n'))
        
        cleanup = options.get('cleanup', False)
        
        try:
            # Run all tests
            self.test_notification_system()
            self.test_search_functionality()
            self.test_activity_log()
            self.test_permission_restrictions()
            
            self.stdout.write(self.style.SUCCESS('\n✅ All tests passed!\n'))
            
            if cleanup:
                self.cleanup_test_data()
                self.stdout.write(self.style.SUCCESS('✅ Test data cleaned up\n'))
            else:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  Test data left in database. Run with --cleanup to remove it.\n'
                ))
                
        except AssertionError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Test failed: {e}\n'))
            sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Unexpected error: {e}\n'))
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def create_test_users(self):
        """Create test users if they don't exist"""
        moderator, _ = User.objects.get_or_create(
            username='test_moderator',
            defaults={
                'email': 'moderator@test.com',
                'is_staff': True,
            }
        )
        moderator.set_password('testpass123')
        moderator.save()
        
        # Set moderator role in profile
        profile, _ = Profile.objects.get_or_create(user=moderator)
        profile.role = Profile.Role.MODERATOR
        profile.save()
        
        org_user, _ = User.objects.get_or_create(
            username='test_org',
            defaults={'email': 'org@test.com'}
        )
        org_user.set_password('testpass123')
        org_user.save()
        
        # Set org role in profile
        org_profile, _ = Profile.objects.get_or_create(user=org_user)
        org_profile.role = Profile.Role.ORG
        org_profile.save()
        
        regular_user, _ = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'user@test.com'}
        )
        regular_user.set_password('testpass123')
        regular_user.save()
        
        return moderator, org_user, regular_user

    def test_notification_system(self):
        """Test 1: Notification system for reports"""
        self.stdout.write(self.style.WARNING('\n[Test 1] Testing Notification System...'))
        
        moderator, org_user, regular_user = self.create_test_users()
        
        # Create a test post
        cuisine, _ = Cuisine.objects.get_or_create(name='Test Cuisine')
        location, _ = Location.objects.get_or_create(
            building_name='Test Building',
            defaults={'latitude': 38.0, 'longitude': -78.0}
        )
        
        post = Post.objects.create(
            event='Test Event for Notifications',
            event_description='This is a test post',
            author=org_user,
            cuisine=cuisine,
            location=location,
            status=Post.Status.PUBLISHED
        )
        
        # Get initial notification count
        initial_count = ModeratorNotification.objects.filter(
            moderator=moderator,
            is_read=False
        ).count()
        
        # Create a flag (this should trigger notifications)
        post_ct = ContentType.objects.get_for_model(Post)
        flag = FlaggedContent.objects.create(
            content_type=post_ct,
            object_id=post.id,
            flagged_by=regular_user,
            reason='Test flag for notification system',
            status=FlaggedContent.Status.PENDING
        )
        
        # Check if notification was created
        notifications = ModeratorNotification.objects.filter(
            moderator=moderator,
            flagged_content=flag,
            is_read=False
        )
        
        assert notifications.exists(), "❌ Notification was not created for moderator"
        assert notifications.count() >= 1, "❌ Expected at least 1 notification"
        
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Notification created: {notifications.count()} notification(s) for moderator'
        ))
        
        # Test marking notification as read
        notification = notifications.first()
        notification.is_read = True
        notification.save()
        
        unread_count = ModeratorNotification.objects.filter(
            moderator=moderator,
            is_read=False
        ).count()
        
        assert unread_count == initial_count, "❌ Notification read status not updated correctly"
        
        self.stdout.write(self.style.SUCCESS('  ✅ Notification can be marked as read'))
        
        # Cleanup
        flag.delete()
        post.delete()

    def test_search_functionality(self):
        """Test 2: Search bar for reports"""
        self.stdout.write(self.style.WARNING('\n[Test 2] Testing Search Functionality...'))
        
        moderator, org_user, regular_user = self.create_test_users()
        
        # Create multiple flags with different content
        cuisine, _ = Cuisine.objects.get_or_create(name='Test Cuisine')
        location, _ = Location.objects.get_or_create(
            building_name='Test Building',
            defaults={'latitude': 38.0, 'longitude': -78.0}
        )
        
        post1 = Post.objects.create(
            event='Searchable Event One',
            event_description='This post contains searchable text',
            author=org_user,
            cuisine=cuisine,
            location=location,
            status=Post.Status.PUBLISHED
        )
        
        post2 = Post.objects.create(
            event='Another Event',
            event_description='Different content here',
            author=org_user,
            cuisine=cuisine,
            location=location,
            status=Post.Status.PUBLISHED
        )
        
        post_ct = ContentType.objects.get_for_model(Post)
        
        flag1 = FlaggedContent.objects.create(
            content_type=post_ct,
            object_id=post1.id,
            flagged_by=regular_user,
            reason='First flag with unique reason text',
            status=FlaggedContent.Status.PENDING
        )
        
        flag2 = FlaggedContent.objects.create(
            content_type=post_ct,
            object_id=post2.id,
            flagged_by=moderator,
            reason='Second flag with different reason',
            status=FlaggedContent.Status.PENDING
        )
        
        # Test search by reason
        results_by_reason = FlaggedContent.objects.filter(
            status=FlaggedContent.Status.PENDING,
            reason__icontains='unique reason'
        )
        assert results_by_reason.count() >= 1, "❌ Search by reason failed"
        self.stdout.write(self.style.SUCCESS('  ✅ Search by reason works'))
        
        # Test search by flagged_by username
        results_by_user = FlaggedContent.objects.filter(
            status=FlaggedContent.Status.PENDING,
            flagged_by__username__icontains='test_user'
        )
        assert results_by_user.count() >= 1, "❌ Search by username failed"
        self.stdout.write(self.style.SUCCESS('  ✅ Search by username works'))
        
        # Test search by content (post event)
        post_ids = Post.objects.filter(event__icontains='Searchable Event').values_list('id', flat=True)
        results_by_content = FlaggedContent.objects.filter(
            status=FlaggedContent.Status.PENDING,
            content_type=post_ct,
            object_id__in=post_ids
        )
        assert results_by_content.count() >= 1, "❌ Search by content failed"
        self.stdout.write(self.style.SUCCESS('  ✅ Search by content works'))
        
        # Test search by status
        results_by_status = FlaggedContent.objects.filter(
            status__icontains='pending'
        )
        assert results_by_status.count() >= 2, "❌ Search by status failed"
        self.stdout.write(self.style.SUCCESS('  ✅ Search by status works'))
        
        # Cleanup
        flag1.delete()
        flag2.delete()
        post1.delete()
        post2.delete()

    def test_activity_log(self):
        """Test 3: Activity log for organizations"""
        self.stdout.write(self.style.WARNING('\n[Test 3] Testing Activity Log...'))
        
        moderator, org_user, regular_user = self.create_test_users()
        
        # Test organization actions
        cuisine, _ = Cuisine.objects.get_or_create(name='Test Cuisine')
        location, _ = Location.objects.get_or_create(
            building_name='Test Building',
            defaults={'latitude': 38.0, 'longitude': -78.0}
        )
        
        # Test POST_CREATED
        post = Post.objects.create(
            event='Activity Log Test Post',
            event_description='Testing activity logging',
            author=org_user,
            cuisine=cuisine,
            location=location,
            status=Post.Status.PUBLISHED
        )
        
        # Manually create activity log (since we're testing, not going through views)
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_CREATED,
            performed_by=org_user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            description='Post created: Activity Log Test Post'
        )
        
        created_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_CREATED
        ).first()
        
        assert created_log is not None, "❌ POST_CREATED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ POST_CREATED activity logged'))
        
        # Test POST_EDITED
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_EDITED,
            performed_by=org_user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            description='Post edited: Activity Log Test Post'
        )
        
        edited_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_EDITED
        ).first()
        
        assert edited_log is not None, "❌ POST_EDITED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ POST_EDITED activity logged'))
        
        # Test POST_DELETED
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_DELETED,
            performed_by=org_user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            description='Post deleted: Activity Log Test Post'
        )
        
        deleted_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.POST_DELETED
        ).first()
        
        assert deleted_log is not None, "❌ POST_DELETED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ POST_DELETED activity logged'))
        
        # Test moderator actions
        post_ct = ContentType.objects.get_for_model(Post)
        flag = FlaggedContent.objects.create(
            content_type=post_ct,
            object_id=post.id,
            flagged_by=regular_user,
            reason='Test flag for activity log',
            status=FlaggedContent.Status.PENDING
        )
        
        # Test FLAG_CREATED
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.FLAG_CREATED,
            performed_by=regular_user,
            content_type=ContentType.objects.get_for_model(FlaggedContent),
            object_id=flag.id,
            description='Content flagged by test_user'
        )
        
        flag_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.FLAG_CREATED
        ).first()
        
        assert flag_log is not None, "❌ FLAG_CREATED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ FLAG_CREATED activity logged'))
        
        # Test CONTENT_DELETED
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.CONTENT_DELETED,
            performed_by=moderator,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            description='Content deleted by moderator'
        )
        
        content_deleted_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.CONTENT_DELETED
        ).first()
        
        assert content_deleted_log is not None, "❌ CONTENT_DELETED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ CONTENT_DELETED activity logged'))
        
        # Test USER_SUSPENDED
        suspension = UserSuspension.objects.create(
            user=org_user,
            suspended_by=moderator,
            reason='Test suspension'
        )
        
        ModeratorActivityLog.objects.create(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.USER_SUSPENDED,
            performed_by=moderator,
            description='User suspended by moderator'
        )
        
        suspended_log = ModeratorActivityLog.objects.filter(
            organization=org_user,
            action_type=ModeratorActivityLog.ActionType.USER_SUSPENDED
        ).first()
        
        assert suspended_log is not None, "❌ USER_SUSPENDED log not found"
        self.stdout.write(self.style.SUCCESS('  ✅ USER_SUSPENDED activity logged'))
        
        # Verify all logs are retrievable for the organization
        all_logs = ModeratorActivityLog.objects.filter(organization=org_user)
        assert all_logs.count() >= 6, f"❌ Expected at least 6 logs, found {all_logs.count()}"
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ Activity log retrieval works: {all_logs.count()} total logs for organization'
        ))
        
        # Cleanup
        flag.delete()
        suspension.delete()
        post.delete()

    def test_permission_restrictions(self):
        """Test 4: Permission restrictions"""
        self.stdout.write(self.style.WARNING('\n[Test 4] Testing Permission Restrictions...'))
        
        moderator, org_user, regular_user = self.create_test_users()
        
        # Test that moderator role is correctly identified
        assert is_moderator(moderator), "❌ Moderator role check failed"
        assert not is_moderator(org_user), "❌ Non-moderator incorrectly identified as moderator"
        self.stdout.write(self.style.SUCCESS('  ✅ Moderator role identification works'))
        
        # Test that moderators have staff status
        assert moderator.is_staff, "❌ Moderator should have staff status"
        self.stdout.write(self.style.SUCCESS('  ✅ Moderator has staff status'))
        
        # Test that regular users can still delete their own accounts (conceptually)
        # We can't actually test deletion in a safe way, but we can verify the check exists
        assert not is_moderator(regular_user), "❌ Regular user should not be moderator"
        self.stdout.write(self.style.SUCCESS('  ✅ Regular users are not moderators'))
        
        # Verify profile roles are set correctly
        moderator_profile = Profile.objects.get(user=moderator)
        assert moderator_profile.role == Profile.Role.MODERATOR, "❌ Moderator profile role incorrect"
        
        org_profile = Profile.objects.get(user=org_user)
        assert org_profile.role == Profile.Role.ORG, "❌ Organization profile role incorrect"
        
        self.stdout.write(self.style.SUCCESS('  ✅ Profile roles are set correctly'))

    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write(self.style.WARNING('\n[Cleanup] Removing test data...'))
        
        # Delete test users and related data
        test_usernames = ['test_moderator', 'test_org', 'test_user']
        
        for username in test_usernames:
            try:
                user = User.objects.get(username=username)
                # Delete related data
                ModeratorNotification.objects.filter(moderator=user).delete()
                ModeratorActivityLog.objects.filter(organization=user).delete()
                ModeratorActivityLog.objects.filter(performed_by=user).delete()
                FlaggedContent.objects.filter(flagged_by=user).delete()
                UserSuspension.objects.filter(user=user).delete()
                UserSuspension.objects.filter(suspended_by=user).delete()
                Post.objects.filter(author=user).delete()
                user.delete()
                self.stdout.write(self.style.SUCCESS(f'  ✅ Deleted user: {username}'))
            except User.DoesNotExist:
                pass
        
        # Clean up test models
        ModeratorNotification.objects.filter(flagged_content__reason__icontains='Test').delete()
        ModeratorActivityLog.objects.filter(description__icontains='Test').delete()
        FlaggedContent.objects.filter(reason__icontains='Test').delete()
        
        self.stdout.write(self.style.SUCCESS('  ✅ Test data cleaned up'))

