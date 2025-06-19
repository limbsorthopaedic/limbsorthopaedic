
from django.db import models
from django.contrib.auth.models import User
import uuid

class ChatMessage(models.Model):
    """Model to store chat messages"""
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for conversation tracking
    conversation_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_messages')
    session_key = models.CharField(max_length=40, blank=True, null=True, help_text="Session key for anonymous users")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.user_message[:30]}..."
