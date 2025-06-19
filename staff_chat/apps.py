from django.apps import AppConfig


class StaffChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff_chat'
    verbose_name = 'Staff Communication'
    
    def ready(self):
        # Import signal handlers
        import staff_chat.signals