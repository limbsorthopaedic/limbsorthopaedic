
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.utils import get_users_with_birthday_today, send_birthday_email


class Command(BaseCommand):
    help = 'Send birthday emails to users who have a birthday today'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which users would receive birthday emails without actually sending them',
        )

    def handle(self, *args, **options):
        users_with_birthday = get_users_with_birthday_today()
        
        if not users_with_birthday.exists():
            self.stdout.write(
                self.style.SUCCESS('No users have birthdays today.')
            )
            return

        self.stdout.write(
            f'Found {users_with_birthday.count()} users with birthdays today:'
        )

        for user in users_with_birthday:
            birthday_date = user.profile.date_of_birth if hasattr(user, 'profile') else None
            self.stdout.write(f'  - {user.get_full_name() or user.username} ({user.email}) - Born: {birthday_date}')

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No emails were sent.')
            )
            return

        # Send birthday emails
        sent_count = 0
        failed_count = 0

        for user in users_with_birthday:
            try:
                result = send_birthday_email(user)
                if result:
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Birthday email sent to {user.email}')
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send birthday email to {user.email}')
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error sending birthday email to {user.email}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Birthday email sending completed. Sent: {sent_count}, Failed: {failed_count}'
            )
        )
