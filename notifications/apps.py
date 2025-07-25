from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = "Notifications"
    
    def ready(self):
        # Import signals to ensure they are connected
        import notifications.signals