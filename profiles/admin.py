from django.contrib import admin
from django.utils.html import format_html
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_username', 'get_email', 'role', 'display_name', 'is_staff_status', 'is_superuser_status')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'display_name')
    list_editable = ('role',)  # Allow quick role changes
    actions = ['make_moderator', 'remove_moderator', 'make_student', 'make_org']
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def is_staff_status(self, obj):
        """Display staff/admin access status"""
        if obj.user.is_staff:
            return format_html('<span style="color: green; font-weight: bold;">✓ Staff</span>')
        else:
            return format_html('<span style="color: gray;">✗ Not Staff</span>')
    is_staff_status.short_description = 'Admin Access'
    
    def is_superuser_status(self, obj):
        """Display superuser status"""
        if obj.user.is_superuser:
            return format_html('<span style="color: red; font-weight: bold;">Superuser</span>')
        else:
            return format_html('<span style="color: gray;">—</span>')
    is_superuser_status.short_description = 'Superuser'
    
    def make_moderator(self, request, queryset):
        """Bulk action: Appoint selected users as moderators (grants admin access)"""
        count = 0
        for profile in queryset:
            if profile.role != Profile.Role.MODERATOR:
                profile.role = Profile.Role.MODERATOR
                profile.save()
                # Signal will automatically set is_staff = True
                count += 1
        self.message_user(request, f'✅ {count} user(s) appointed as moderators. They now have admin access.')
    make_moderator.short_description = "👑 Appoint as Moderator (grants admin access)"
    
    def remove_moderator(self, request, queryset):
        """Bulk action: Remove moderator status (removes admin access)"""
        count = 0
        for profile in queryset:
            if profile.role == Profile.Role.MODERATOR:
                profile.role = None
                profile.save()
                # Signal will automatically remove is_staff if not superuser
                count += 1
        self.message_user(request, f'✅ {count} user(s) removed from moderator role. Admin access revoked.')
    remove_moderator.short_description = "🗑️ Remove Moderator Status"
    
    def make_student(self, request, queryset):
        """Bulk action: Set selected users as students"""
        count = 0
        for profile in queryset:
            if profile.role != Profile.Role.STUDENT:
                profile.role = Profile.Role.STUDENT
                profile.save()
                count += 1
        self.message_user(request, f'✅ {count} user(s) set as students.')
    make_student.short_description = "👨‍🎓 Set as Student"
    
    def make_org(self, request, queryset):
        """Bulk action: Set selected users as organizations"""
        count = 0
        for profile in queryset:
            if profile.role != Profile.Role.ORG:
                profile.role = Profile.Role.ORG
                profile.save()
                count += 1
        self.message_user(request, f'✅ {count} user(s) set as organizations.')
    make_org.short_description = "🏢 Set as Organization"
