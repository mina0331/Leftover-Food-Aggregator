from django.contrib import admin
from django.contrib.admin.models import LogEntry

# Register your models here.

# Register LogEntry so moderators can view admin action logs
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing Django admin action logs.
    Allows moderators to see who did what, when.
    """
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'get_change_message_display')
    list_filter = ('action_time', 'action_flag', 'content_type')
    search_fields = ('user__username', 'object_repr', 'change_message')
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
    date_hierarchy = 'action_time'
    
    def has_view_permission(self, request, obj=None):
        """Allow staff/moderators to view log entries"""
        return request.user.is_staff
    
    def has_add_permission(self, request):
        """Log entries are created automatically, not manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Log entries are read-only"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of log entries (for cleanup)"""
        return request.user.is_staff
    
    def get_change_message_display(self, obj):
        """Display a readable version of the change message"""
        if obj.change_message:
            try:
                import json
                change_data = json.loads(obj.change_message)
                if isinstance(change_data, list):
                    return ', '.join([str(c) for c in change_data])
            except (json.JSONDecodeError, TypeError):
                pass
            return obj.change_message[:100] + '...' if len(obj.change_message) > 100 else obj.change_message
        return '—'
    get_change_message_display.short_description = 'Change Message'
