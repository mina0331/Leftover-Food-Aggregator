from django.contrib import admin
from .models import FlaggedContent, UserSuspension, ModeratorNotification, ModeratorActivityLog


@admin.register(FlaggedContent)
class FlaggedContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_content_type', 'get_content_preview', 'flagged_by', 'status', 'flagged_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'flagged_at', 'reviewed_at', 'content_type')
    search_fields = ('reason', 'moderator_notes', 'flagged_by__username', 'reviewed_by__username')
    readonly_fields = ('content_type', 'object_id', 'flagged_by', 'flagged_at', 'reviewed_by', 'reviewed_at')
    fieldsets = (
        ('Content Information', {
            'fields': ('content_type', 'object_id', 'get_content_preview')
        }),
        ('Flag Details', {
            'fields': ('flagged_by', 'reason', 'flagged_at')
        }),
        ('Moderation', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'moderator_notes')
        }),
    )
    
    def get_content_type(self, obj):
        return obj.get_content_type_name()
    get_content_type.short_description = 'Content Type'
    
    def get_content_preview(self, obj):
        if obj.content_object:
            return str(obj.content_object)[:100]
        return "Content deleted"
    get_content_preview.short_description = 'Content Preview'
    
    def has_add_permission(self, request):
        return False  # Flags should only be created through the flagging interface


@admin.register(UserSuspension)
class UserSuspensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'suspended_by', 'is_active', 'suspended_at', 'get_duration_display', 'reinstated_at')
    list_filter = ('is_active', 'suspended_at', 'reinstated_at', 'suspended_by')
    search_fields = ('user__username', 'user__email', 'reason', 'reinstatement_notes')
    readonly_fields = ('suspended_at', 'reinstated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'suspended_by')
        }),
        ('Suspension Details', {
            'fields': ('reason', 'suspended_at', 'suspended_until', 'is_active')
        }),
        ('Reinstatement', {
            'fields': ('reinstated_by', 'reinstated_at', 'reinstatement_notes')
        }),
    )
    
    def get_duration_display(self, obj):
        return obj.get_duration_display()
    get_duration_display.short_description = 'Duration'


@admin.register(ModeratorNotification)
class ModeratorNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'moderator', 'flagged_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'moderator')
    search_fields = ('moderator__username', 'flagged_content__reason')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False  # Notifications are created automatically via signals


@admin.register(ModeratorActivityLog)
class ModeratorActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'action_type', 'performed_by', 'created_at', 'get_related_content')
    list_filter = ('action_type', 'created_at', 'organization')
    search_fields = ('organization__username', 'performed_by__username', 'description')
    readonly_fields = ('created_at', 'content_type', 'object_id')
    date_hierarchy = 'created_at'
    
    def get_related_content(self, obj):
        if obj.related_content:
            return str(obj.related_content)[:50]
        return "—"
    get_related_content.short_description = 'Related Content'
    
    def has_add_permission(self, request):
        return False  # Activity logs are created automatically
