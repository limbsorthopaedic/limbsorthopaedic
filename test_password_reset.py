"""
Script to test the password reset functionality.
This will test the password reset email sending functionality.
It will use the file-based email backend to avoid sending real emails.

Usage:
python test_password_reset.py
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limbs_orthopaedic.settings')

# Initialize Django
django.setup()

# Override email backend settings after django.setup()
from django.conf import settings
from django.test.utils import override_settings

# Import Django modules after setup
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Import our custom email function
from accounts.utils import send_password_reset_email

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
    EMAIL_FILE_PATH='sent_emails'
)
def test_password_reset():
    """Test the password reset email functionality"""
    print("Testing password reset email...")
    print(f"Using email backend: {settings.EMAIL_BACKEND}")
    print(f"Email file path: {settings.EMAIL_FILE_PATH}")
    
    # Get or create a test user
    email = 'mail@limbsorthopaedic.org'
    try:
        user = User.objects.get(email=email)
        print(f"Using existing user: {user.username} <{user.email}>")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testreset',
            email=email,
            password='test@paSsword123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created new test user: {user.username} <{user.email}>")
    
    # Generate token and UID for password reset
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Send password reset email
    try:
        result = send_password_reset_email(user, token, uid)
        if result:
            print("✅ Password reset email sent successfully!")
            print(f"Check the sent_emails directory for the email content.")
        else:
            print("❌ Failed to send password reset email.")
    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")

if __name__ == "__main__":
    # Create sent_emails directory if it doesn't exist
    os.makedirs('sent_emails', exist_ok=True)
    
    # Test password reset email
    test_password_reset()