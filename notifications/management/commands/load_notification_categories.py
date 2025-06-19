from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load initial notification categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Loading initial notification categories...'))
        call_command('loaddata', 'initial_categories.json', app_label='notifications')
        self.stdout.write(self.style.SUCCESS('Successfully loaded notification categories'))