from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from notifications.models import NotificationCategory, Notification


class Command(BaseCommand):
    help = 'Generate test notifications for each category'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of notifications to generate per category'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.NOTICE(f'Generating {count} test notifications per category...'))
        
        # Get all categories
        categories = NotificationCategory.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.WARNING('No notification categories found. Run load_notification_categories first.'))
            return
        
        total_generated = 0
        
        for category in categories:
            try:
                # Get the model class for this category
                model_class = apps.get_model(category.app_label, category.model_name)
                content_type = ContentType.objects.get_for_model(model_class)
                
                # Get some objects of this model if any exist
                objects = model_class.objects.all()[:count]
                
                if not objects:
                    self.stdout.write(self.style.WARNING(
                        f'No objects found for {category.app_label}.{category.model_name}'))
                    continue
                
                # Generate notifications for each object
                for obj in objects:
                    # Create more meaningful notifications based on the category
                    if category.name == 'appointment':
                        message = f'New appointment scheduled with {obj}'
                    elif category.name == 'blog_comment':
                        message = f'New comment received on blog post {obj}'
                    elif category.name == 'testimonial':
                        message = f'New testimonial submitted by {obj}'
                    elif category.name == 'contact':
                        message = f'New contact form submission from {obj}'
                    elif category.name == 'product_inquiry':
                        message = f'New product inquiry about {obj}'
                    else:
                        message = f'New {category.name} notification: {obj}'
                        
                    notification = Notification.objects.create(
                        category=category,
                        content_type=content_type,
                        object_id=obj.pk,
                        message=message
                    )
                    total_generated += 1
                    self.stdout.write(f'Created notification: {notification.message}')
                
            except (LookupError, ContentType.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(
                    f'Error creating notifications for {category.name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully generated {total_generated} test notifications'))