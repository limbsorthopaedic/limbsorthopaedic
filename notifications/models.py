from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse


class NotificationCategory(models.Model):
    """
    Categories for different types of notifications (appointments, comments, etc.)
    """
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, default="Notification")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=20, default='primary')
    app_label = models.CharField(max_length=100, help_text="Django app label for this category")
    model_name = models.CharField(max_length=100, help_text="Model name for this category")
    admin_url_name = models.CharField(
        max_length=100, 
        help_text="Admin URL name for this model (e.g., 'admin:app_model_changelist')",
        blank=True
    )
    
    class Meta:
        verbose_name = "Notification Category"
        verbose_name_plural = "Notification Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.display_name
    
    def get_absolute_url(self):
        """Return the admin URL for this category's model changelist"""
        if self.admin_url_name:
            try:
                return reverse(self.admin_url_name)
            except:
                pass
        return reverse('admin:index')


class Notification(models.Model):
    """
    Generic notification model that can reference any model instance
    """
    category = models.ForeignKey(
        NotificationCategory, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Generic foreign key to the related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Notification details
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return self.message
    
    def mark_as_read(self):
        """Mark this notification as read"""
        self.is_read = True
        self.save()
    
    def get_admin_url(self):
        """Get admin URL for the related object"""
        from django.apps import apps
        
        if not self.content_type or not self.object_id:
            return '#'
        
        model = self.content_type.model_class()
        app_label = self.content_type.app_label
        
        try:
            url_name = f'admin:{app_label}_{model.__name__.lower()}_change'
            return reverse(url_name, args=[self.object_id])
        except:
            return '#'


# Helper functions for notification management
def get_unread_count():
    """Get count of unread notifications"""
    return Notification.objects.filter(is_read=False).count()

def get_unread_by_category():
    """Get counts of unread notifications by category"""
    from django.db.models import Count
    return NotificationCategory.objects.filter(
        notifications__is_read=False
    ).annotate(unread_count=Count('notifications')).values('id', 'name', 'display_name', 'unread_count')

def mark_all_as_read():
    """Mark all notifications as read"""
    return Notification.objects.filter(is_read=False).update(is_read=True)