from django.contrib import admin
from .models import FlaggedContent, UserSuspension


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
