
from django.core.management.base import BaseCommand
from limbs_cyber.models import ProductService


class Command(BaseCommand):
    help = 'Setup initial products and services for Limbs Cyber POS'

    def handle(self, *args, **kwargs):
        products = [
            {'name': 'Envelopes', 'category': 'product', 'unit_price': 10, 'current_stock': 100},
            {'name': 'Lamination', 'category': 'service', 'unit_price': 70, 'current_stock': 999},
            {'name': 'Passport Application (eCitizen)', 'category': 'service', 'unit_price': 500, 'current_stock': 999},
            {'name': 'Filing KRA Returns (Employed)', 'category': 'service', 'unit_price': 250, 'current_stock': 999},
            {'name': 'Photocopying (Black & White)', 'category': 'service', 'unit_price': 5, 'current_stock': 999},
            {'name': 'Photocopying (Color)', 'category': 'service', 'unit_price': 20, 'current_stock': 999},
            {'name': 'Printing (Black & White)', 'category': 'service', 'unit_price': 10, 'current_stock': 999},
            {'name': 'Printing (Color)', 'category': 'service', 'unit_price': 30, 'current_stock': 999},
            {'name': 'Scanning', 'category': 'service', 'unit_price': 20, 'current_stock': 999},
            {'name': 'Typing Services', 'category': 'service', 'unit_price': 50, 'current_stock': 999},
            {'name': 'Binding (Spiral)', 'category': 'service', 'unit_price': 100, 'current_stock': 999},
            {'name': 'Binding (Hard Cover)', 'category': 'service', 'unit_price': 300, 'current_stock': 999},
        ]

        created_count = 0
        for product_data in products:
            product, created = ProductService.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nSetup complete! Created {created_count} new items.'))
