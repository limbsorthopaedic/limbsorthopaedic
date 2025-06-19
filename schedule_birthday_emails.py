
#!/usr/bin/env python
"""
Script to set up automatic birthday email sending.
This can be run daily via cron job or similar scheduling system.

Add this to your cron tab (run `crontab -e`):
0 9 * * * cd /path/to/your/project && python manage.py send_birthday_emails

This will check for birthdays and send emails every day at 9 AM.
"""

import os
import sys
import django

# Set up Django environment
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
    django.setup()
    
    # Import Django management
    from django.core.management import call_command
    
    print("Checking for birthday emails to send...")
    call_command('send_birthday_emails')
    print("Birthday email check completed.")
