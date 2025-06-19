from django.contrib import admin
from django.utils.html import format_html
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'truncated_user_message', 'created_at', 'conversation_id')
    readonly_fields = ('user_message', 'ai_response', 'created_at', 'conversation_id', 'user', 'session_key')
    list_filter = ('created_at', 'user')
    search_fields = ('user_message', 'ai_response', 'conversation_id')
    date_hierarchy = 'created_at'
    
    def truncated_user_message(self, obj):
        return obj.user_message[:50] + ("..." if len(obj.user_message) > 50 else "")
    truncated_user_message.short_description = 'User Message'
    
    def get_user(self, obj):
        if obj.user:
            return obj.user.username
        return "Anonymous"
    get_user.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
        
    actions = ['export_as_text']
    
    def export_as_text(self, request, queryset):
        """Export selected messages as a single text file"""
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="chat_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.txt"'
        
        conversation_id = None
        if queryset.count() > 0:
            # Check if all messages have the same conversation_id
            conversation_ids = queryset.values_list('conversation_id', flat=True).distinct()
            if conversation_ids.count() == 1 and conversation_ids[0]:
                conversation_id = conversation_ids[0]
        
        if conversation_id:
            response.write(f"Chat Conversation ID: {conversation_id}\n")
            response.write(f"Exported on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        else:
            response.write(f"Chat Export\n")
            response.write(f"Exported on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
        # Sort by creation time
        messages = queryset.order_by('created_at')
        
        for msg in messages:
            response.write(f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}]\n")
            response.write(f"User: {msg.user_message}\n")
            response.write(f"AI: {msg.ai_response}\n\n")
            
        return response
        
    export_as_text.short_description = "Export selected messages as text"
