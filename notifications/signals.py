from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from .models import Notification, NotificationCategory

def create_notification(instance, message=None, category_name=None):
    """
    Create a notification for the given model instance.
    
    Args:
        instance: The model instance to create a notification for
        message: Optional custom message, otherwise will use str(instance)
        category_name: Optional category name, otherwise will try to determine from instance
    """
    # Get content type
    content_type = ContentType.objects.get_for_model(instance)
    
    # Try to determine category if not provided
    if not category_name:
        app_label = content_type.app_label
        model_name = content_type.model
        try:
            category = NotificationCategory.objects.get(
                app_label=app_label, 
                model_name=model_name
            )
        except NotificationCategory.DoesNotExist:
            # No category exists for this model, can't create notification
            return None
    else:
        try:
            category = NotificationCategory.objects.get(name=category_name)
        except NotificationCategory.DoesNotExist:
            # Specified category doesn't exist
            return None
    
    # Create notification with default message if none provided
    if not message:
        message = f"New {category.display_name}: {str(instance)}"
    
    notification = Notification.objects.create(
        category=category,
        content_type=content_type,
        object_id=instance.pk,
        message=message
    )
    
    return notification

# Connect signals for different models that should create notifications
def connect_notification_signals():
    """Connect all relevant model signals for notifications"""
    # Get all notification categories
    for category in NotificationCategory.objects.all():
        try:
            # Get the model class for this category
            model_class = apps.get_model(category.app_label, category.model_name)
            
            # Define a receiver function specific to this model
            @receiver(post_save, sender=model_class)
            def model_saved(sender, instance, created, **kwargs):
                if created:  # Only notify on creation, not updates
                    create_notification(instance, category_name=category.name)
        
        except LookupError:
            # Model doesn't exist, skip it
            continue