from django.contrib import admin
from django.utils.html import format_html
from .models import StaffGroup, StaffGroupMember, StaffChatMessage, ChatAttachment

class StaffGroupMemberInline(admin.TabularInline):
    model = StaffGroupMember
    extra = 1
    fields = ('user', 'is_admin', 'is_active', 'joined_at', 'last_read_at')
    readonly_fields = ('joined_at', 'last_read_at')
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the last admin member
        return True

class ChatAttachmentInline(admin.TabularInline):
    model = ChatAttachment
    extra = 0
    fields = ('file', 'file_name', 'file_type', 'file_size', 'get_file_display', 'uploaded_at')
    readonly_fields = ('file_name', 'file_type', 'file_size', 'get_file_display', 'uploaded_at')
    
    def get_file_display(self, obj):
        """Display a preview or icon for the file"""
        if not obj.file:
            return '-'
        
        if obj.file_type and obj.file_type.startswith('image/'):
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;">', obj.file.url)
        else:
            icon_class = obj.get_icon_class()
            return format_html('<i class="{}" style="font-size: 24px;"></i> {}', icon_class, obj.file_name)
    
    get_file_display.short_description = 'Preview'

@admin.register(StaffGroup)
class StaffGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'members_count', 'messages_count', 'created_at')
    search_fields = ('name', 'description')
    inlines = [StaffGroupMemberInline]
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members'
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Messages'

@admin.register(StaffGroupMember)
class StaffGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_admin', 'is_active', 'joined_at', 'last_activity')
    list_filter = ('group', 'is_admin', 'is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('joined_at', 'last_read_at')
    
    def last_activity(self, obj):
        return obj.last_read_at.strftime('%b %d, %Y at %I:%M %p')
    last_activity.short_description = 'Last Read'

@admin.register(StaffChatMessage)
class StaffChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'message_preview', 'has_attachments', 'is_system_message', 'created_at')
    list_filter = ('group', 'is_system_message', 'created_at')
    search_fields = ('sender__username', 'sender__email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChatAttachmentInline]
    
    def sender_name(self, obj):
        if obj.is_system_message:
            return format_html('<span style="color: #6c757d;"><i class="fas fa-robot"></i> System</span>')
        return obj.sender.get_full_name() or obj.sender.username
    sender_name.short_description = 'Sender'
    
    def message_preview(self, obj):
        max_length = 50
        message = obj.message
        if len(message) > max_length:
            return message[:max_length] + '...'
        return message
    message_preview.short_description = 'Message'
    
    def has_attachments(self, obj):
        has_attachments = obj.attachments.exists()
        if has_attachments:
            return format_html('<span style="color: green;"><i class="fas fa-check"></i></span>')
        return format_html('<span style="color: #6c757d;">-</span>')
    has_attachments.short_description = 'Attachments'

@admin.register(ChatAttachment)
class ChatAttachmentAdmin(admin.ModelAdmin):
    list_display = ('message_sender', 'file_name', 'file_type', 'get_formatted_size', 'get_file_display', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name', 'message__sender__username', 'message__message')
    readonly_fields = ('file_name', 'file_type', 'file_size', 'get_file_display', 'uploaded_at')
    
    def message_sender(self, obj):
        if obj.message.is_system_message:
            return format_html('<span style="color: #6c757d;"><i class="fas fa-robot"></i> System</span>')
        return obj.message.sender.get_full_name() or obj.message.sender.username
    message_sender.short_description = 'Sender'
    
    def get_file_display(self, obj):
        """Display a preview or icon for the file"""
        if not obj.file:
            return '-'
        
        if obj.file_type and obj.file_type.startswith('image/'):
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;">', obj.file.url)
        else:
            icon_class = obj.get_icon_class()
            return format_html('<i class="{}" style="font-size: 24px;"></i> {}', icon_class, obj.file_name)
    
    get_file_display.short_description = 'Preview'