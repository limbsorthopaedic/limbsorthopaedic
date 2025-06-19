"""
Utility functions for the accounts app
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

def send_welcome_email(user):
    """
    Send a welcome email to newly registered users
    """
    subject = 'Welcome to LIMBS Orthopaedic!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    # Enhanced debug log
    print(f"Sending welcome email to {to_email} from {from_email}")
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
    print(f"Email host: {settings.EMAIL_HOST}")
    print(f"Email port: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    # Construct full login URL
    if hasattr(settings, 'HOST_URL') and settings.HOST_URL:
        full_login_url = f"{settings.HOST_URL}{settings.LOGIN_URL}"
    else:
        full_login_url = settings.LOGIN_URL
    
    print(f"Login URL for welcome email: {full_login_url}")
    
    # Render HTML content from template
    html_content = render_to_string('accounts/email/welcome_email.html', {
        'user': user,
        'login_url': full_login_url,
    })
    
    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    # Send the email
    try:
        result = msg.send()
        print(f"Welcome email sent successfully: {result}")
        return result
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # Don't re-raise the exception to avoid breaking the signup process
        # if email sending fails
        return 0


def send_birthday_email(user):
    """
    Send a birthday email to a user
    """
    subject = 'Happy Birthday from LIMBS Orthopaedic! 🎉'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    # Enhanced debug log
    print(f"Sending birthday email to {to_email} from {from_email}")
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
    print(f"Email host: {settings.EMAIL_HOST}")
    print(f"Email port: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    # Render HTML content from template
    html_content = render_to_string('accounts/email/birthday_email.html', {
        'user': user,
    })
    
    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    # Send the email
    try:
        result = msg.send()
        print(f"Birthday email sent successfully: {result}")
        return result
    except Exception as e:
        print(f"Error sending birthday email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return 0


def get_users_with_birthday_today():
    """
    Get all users who have a birthday today
    """
    today = date.today()
    
    # Get users whose profile has a date_of_birth matching today's month and day
    from .models import Profile
    
    users_with_birthday = User.objects.filter(
        profile__date_of_birth__month=today.month,
        profile__date_of_birth__day=today.day,
        is_active=True
    )
    
    return users_with_birthday


def send_custom_email(custom_email, recipient_email):
    """
    Send a custom email to a specific recipient
    """
    from datetime import datetime
    
    subject = custom_email.subject
    from_email = f"{custom_email.sender_name} <{custom_email.sender_email}>"
    to_email = recipient_email
    
    # Debug log
    print(f"Sending custom email '{custom_email.title}' to {to_email} from {from_email}")
    
    # Render HTML content from template
    html_content = render_to_string('accounts/email/custom_email.html', {
        'email': custom_email,
        'recipient_email': recipient_email,
        'current_year': datetime.now().year,
    })
    
    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    # Send the email
    try:
        result = msg.send()
        print(f"Custom email sent successfully to {to_email}: {result}")
        return result
    except Exception as e:
        print(f"Error sending custom email to {to_email}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return 0

def send_password_reset_email(user, token, uid):
    """
    Send a password reset email with the reset link
    """
    subject = 'LIMBS Orthopaedic - Password Reset'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    # Enhanced debug log
    print(f"Sending password reset email to {to_email} from {from_email}")
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
    print(f"Email host: {settings.EMAIL_HOST}")
    print(f"Email port: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    absolute_url = f"{settings.HOST_URL}{reset_url}" if hasattr(settings, 'HOST_URL') else reset_url
    
    print(f"Reset URL: {absolute_url}")
    
    # Render HTML content from template
    html_content = render_to_string('accounts/email/password_reset_email.html', {
        'user': user,
        'reset_url': absolute_url,
        'site_name': 'LIMBS Orthopaedic',
    })
    
    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    # Send the email
    try:
        result = msg.send()
        print(f"Password reset email sent successfully: {result}")
        return result
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # Re-raise the exception for password reset since it needs special handling by the view
        raise

def send_appointment_confirmation_email(appointment):
    """
    Send an appointment confirmation email
    """
    # Set subject based on appointment status
    if appointment.status == 'confirmed':
        subject = 'LIMBS Orthopaedic - Your Appointment is Confirmed'
    else:
        subject = 'LIMBS Orthopaedic - Appointment Booking Received'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # If the appointment is linked to a user, use their email
    if appointment.user:
        to_email = appointment.user.email
    else:
        # Otherwise use the email provided during booking
        to_email = appointment.email
    
    # Debug log
    print(f"Sending appointment email to {to_email} from {from_email}")
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
    print(f"Email host: {settings.EMAIL_HOST}")
    print(f"Email port: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"Appointment status: {appointment.status}")
    
    # Render HTML content from template
    html_content = render_to_string('appointments/email/appointment_confirmation.html', {
        'appointment': appointment,
    })
    
    # Create plain text version by stripping HTML
    text_content = strip_tags(html_content)
    
    # Create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    # Send the email
    try:
        result = msg.send()
        print(f"Appointment email sent successfully: {result}")
        return result
    except Exception as e:
        print(f"Error sending appointment email: {e}")
        print(f"Error type: {type(e).__name__}")
        # Re-raise the exception to be handled by the caller
        raise