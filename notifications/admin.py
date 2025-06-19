from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import NotificationCategory, Notification


@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'app_label', 'model_name', 'notification_count')
    search_fields = ('name', 'display_name', 'app_label', 'model_name')
    list_filter = ('app_label',)
    
    def notification_count(self, obj):
        """Display the count of notifications for this category"""
        count = obj.notifications.count()
        unread = obj.notifications.filter(is_read=False).count()
        if unread > 0:
            return format_html(
                '{} total, <b class="text-danger">{} unread</b>',
                count, unread
            )
        return f"{count} total"
    
    notification_count.short_description = "Notifications"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'category', 'is_read', 'content_link')
    list_filter = ('is_read', 'category', 'created_at')
    search_fields = ('message',)
    readonly_fields = ('created_at', 'updated_at', 'content_type', 'object_id', 'content_link')
    actions = ['mark_as_read', 'mark_as_unread']
    
    def get_queryset(self, request):
        """Allow filtering unread notifications"""
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        """Add a quick filter to show only unread notifications"""
        if not extra_context:
            extra_context = {}
        extra_context['unread_count'] = self.get_queryset(request).filter(is_read=False).count()
        return super().changelist_view(request, extra_context=extra_context)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('message', 'category', 'is_read', 'created_at', 'updated_at')
        }),
        ('Related Content', {
            'fields': ('content_type', 'object_id', 'content_link')
        }),
    )
    
    def content_link(self, obj):
        """
        Generate a link to the related object in the admin
        """
        url = obj.get_admin_url()
        if url == '#':
            return "N/A"
        
        if hasattr(obj.content_object, '__str__'):
            link_text = str(obj.content_object)
        else:
            link_text = f"{obj.content_type.model} #{obj.object_id}"
            
        return format_html('<a href="{0}" target="_blank">{1}</a>', url, link_text)
    
    content_link.short_description = "Related Object"
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")
    
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} notification(s) marked as unread.")
    
    mark_as_unread.short_description = "Mark selected notifications as unread"