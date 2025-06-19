"""
Script to test email functionality using a file-based email backend.
Run with: python test_email.py

This will:
1. Send a test welcome email
2. Create a test appointment and send a confirmation email

All emails will be saved to the 'sent_emails' directory for inspection.
"""
import os
import sys
import django
import datetime

# Create directory to store sent emails
EMAIL_DIR = 'sent_emails'
os.makedirs(EMAIL_DIR, exist_ok=True)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')
# Explicitly set the email backend to file-based to override settings.py
os.environ['DJANGO_EMAIL_BACKEND'] = 'django.core.mail.backends.filebased.EmailBackend'
os.environ['EMAIL_FILE_PATH'] = os.path.join(os.getcwd(), EMAIL_DIR)
print(f"Using file-based email backend. Emails will be saved to: {EMAIL_DIR}")
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from appointments.models import Appointment, Service
from accounts.utils import send_welcome_email, send_appointment_confirmation_email


def test_plain_email():
    """Send a simple plain text email"""
    print("\n=== Testing Plain Email ===")
    result = send_mail(
        subject='Test Email from LIMBS Orthopaedic',
        message='This is a test email from the LIMBS Orthopaedic system.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['mail@limbsorthopaedic.org'],
        fail_silently=False,
    )
    print(f"Email sent: {result}")


def test_html_email():
    """Send an HTML email"""
    print("\n=== Testing HTML Email ===")
    subject = 'HTML Test Email from LIMBS Orthopaedic'
    html_content = """
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background-color: #34bdf2; color: white; padding: 10px; text-align: center; }
                .content { padding: 20px; }
                .footer { font-size: 12px; color: #666; text-align: center; padding: 10px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LIMBS Orthopaedic</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>This is a <strong>test HTML email</strong> from the LIMBS Orthopaedic system.</p>
                <p>The email functionality appears to be working correctly.</p>
            </div>
            <div class="footer">
                <p>LIMBS Orthopaedic - Nairobi, Kenya</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
    </html>
    """
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['mail@limbsorthopaedic.org']
    )
    email.attach_alternative(html_content, "text/html")
    result = email.send()
    print(f"HTML Email sent: {result}")


def test_welcome_email():
    """Test the welcome email template"""
    print("\n=== Testing Welcome Email ===")
    # Create a test user if it doesn't exist
    test_user, created = User.objects.get_or_create(
        username='mail',
        email='mail@limbsorthopaedic.org',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        test_user.set_password('testpassword')
        test_user.save()
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing test user: {test_user.username}")
    
    # Send welcome email
    send_welcome_email(test_user)
    print(f"Welcome email sent and saved to {EMAIL_DIR} directory")


def test_appointment_email():
    """Test appointment confirmation email"""
    print("\n=== Testing Appointment Confirmation Email ===")
    
    # Get or create a test user
    test_user, _ = User.objects.get_or_create(
        username='mail',
        email='mail@limbsorthopaedic.org',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    # Get or create a test service category
    from services.models import ServiceCategory
    test_category, _ = ServiceCategory.objects.get_or_create(
        name='Test Category',
        defaults={
            'description': 'Test category for email testing',
            'slug': 'test-category',
            'is_active': True
        }
    )
    
    # Get or create a test service
    test_service, _ = Service.objects.get_or_create(
        title='Test Service',
        defaults={
            'description': 'This is a test service for email testing',
            'slug': 'test-service',
            'category': test_category,
            'is_active': True
        }
    )
    
    # Create a test appointment
    test_appointment = Appointment.objects.create(
        user=mail,
        full_name='Test Patient',
        email='mail@limbsorthopaedic.org',
        phone='+254719628276',
        service=test_service,
        preferred_date=timezone.now().date() + timezone.timedelta(days=3),
        preferred_time=timezone.now().time(),
        notes='This is a test appointment created for email testing',
        status='pending'
    )
    
    print(f"Created test appointment: {test_appointment}")
    
    # Send confirmation email
    send_appointment_confirmation_email(test_appointment)
    print(f"Appointment booking email sent and saved to {EMAIL_DIR} directory")
    
    # Update status and send another confirmation
    test_appointment.status = 'confirmed'
    test_appointment.save()
    send_appointment_confirmation_email(test_appointment)
    print(f"Appointment confirmed email sent and saved to {EMAIL_DIR} directory")


if __name__ == "__main__":
    print("Starting email tests...")
    test_plain_email()
    test_html_email()
    test_welcome_email()
    test_appointment_email()
    print("\nAll email tests completed.")