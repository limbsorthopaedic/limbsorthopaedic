from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Profile(models.Model):
    """Extended user profile"""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True, help_text="Any relevant medical conditions or allergies")
    profile_image_url = models.URLField(max_length=500, blank=True, null=True, 
                                       help_text="URL for your profile image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_profile_image(self):
        """Return the profile image URL or default icon"""
        if self.profile_image_url:
            return self.profile_image_url
        return None


class Doctor(models.Model):
    """Doctor model extending User model"""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    specialty = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    profile_image_url = models.URLField(max_length=500, blank=True, null=True, 
                                     help_text="Optional external URL for profile image (used if no image is uploaded)")
    office_location = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

    def get_profile_image(self):
        """Return the profile image (either uploaded file or external URL)"""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        elif self.profile_image_url:
            return self.profile_image_url
        return None


class CustomEmail(models.Model):
    """Model for custom emails that can be sent to multiple recipients"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('scheduled', 'Scheduled'),
    )

    title = models.CharField(max_length=200, help_text="Internal title for this email")
    subject = models.CharField(max_length=200, help_text="Email subject line")
    content = CKEditor5Field(help_text="Email content - you can use HTML formatting")
    sender_name = models.CharField(max_length=100, default="LIMBS Orthopaedic Team")
    sender_email = models.EmailField(default="LimbsOrthopaedic@gmail.com")

    # Recipients
    send_to_all_users = models.BooleanField(default=False, help_text="Send to all registered users")
    additional_emails = models.TextField(blank=True, null=True, 
                                       help_text="Additional email addresses (comma-separated)")

    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_send_time = models.DateTimeField(blank=True, null=True, 
                                             help_text="Schedule email for later sending")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_emails_created')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    total_recipients = models.PositiveIntegerField(default=0)
    successful_sends = models.PositiveIntegerField(default=0)
    failed_sends = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"

    def get_recipient_emails(self):
        """Get all email addresses this email should be sent to"""
        emails = set()

        # Add registered users if selected
        if self.send_to_all_users:
            user_emails = User.objects.filter(is_active=True).values_list('email', flat=True)
            emails.update(user_emails)

        # Add selected users
        selected_emails = self.recipients.values_list('user__email', flat=True)
        emails.update(selected_emails)

        # Add additional emails
        if self.additional_emails:
            additional = [email.strip() for email in self.additional_emails.split(',') if email.strip()]
            emails.update(additional)

        return list(emails)


class CustomEmailRecipient(models.Model):
    """Model to track specific users selected as recipients for custom emails"""
    custom_email = models.ForeignKey(CustomEmail, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('custom_email', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.custom_email.title}"


class CustomEmailLog(models.Model):
    """Model to log individual email sends"""
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    custom_email = models.ForeignKey(CustomEmail, on_delete=models.CASCADE, related_name='logs')
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.recipient_email} - {self.status}"