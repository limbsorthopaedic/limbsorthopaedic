from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Profile, Doctor, CustomEmail, CustomEmailRecipient, CustomEmailLog
from .utils import send_custom_email

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_gender')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_gender(self, obj):
        try:
            return obj.profile.get_gender_display()
        except Profile.DoesNotExist:
            return '-'
    get_gender.short_description = 'Gender'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'date_of_birth', 'created_at', 'gender')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'address', 'city', 'date_of_birth')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'office_location', 'is_active', 'created_at')
    list_filter = ('specialty', 'is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'specialty')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'specialty', 'office_location', 'is_active')
        }),
        ('Profile Image', {
            'fields': ('profile_image', 'profile_image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """When a doctor is created or updated, ensure the user is in the correct group"""
        super().save_model(request, obj, form, change)
        # Make sure the user has staff status to access admin site
        if not obj.user.is_staff:
            obj.user.is_staff = True
            obj.user.save()


class CustomEmailRecipientInline(admin.TabularInline):
    model = CustomEmailRecipient
    extra = 0


class CustomEmailLogInline(admin.TabularInline):
    model = CustomEmailLog
    extra = 0
    readonly_fields = ['recipient_email', 'status', 'error_message', 'sent_at']
    can_delete = False


@admin.register(CustomEmail)
class CustomEmailAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'status', 'total_recipients', 'successful_sends', 'failed_sends', 'created_at', 'send_action']
    list_filter = ['status', 'created_at', 'send_to_all_users']
    search_fields = ['title', 'subject', 'content']
    readonly_fields = ['created_by', 'created_at', 'sent_at', 'total_recipients', 'successful_sends', 'failed_sends']
    inlines = [CustomEmailRecipientInline, CustomEmailLogInline]

    fieldsets = (
        ('Email Content', {
            'fields': ('title', 'subject', 'content', 'sender_name', 'sender_email')
        }),
        ('Recipients', {
            'fields': ('send_to_all_users', 'additional_emails'),
            'description': 'Choose recipients: either all users, specific users (add them below), or additional email addresses.'
        }),
        ('Scheduling & Status', {
            'fields': ('status', 'scheduled_send_time'),
        }),
        ('Tracking', {
            'fields': ('total_recipients', 'successful_sends', 'failed_sends', 'created_by', 'created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:email_id>/send/', self.admin_site.admin_view(self.send_email_view), name='accounts_customemail_send'),
            path('<int:email_id>/preview/', self.admin_site.admin_view(self.preview_email_view), name='accounts_customemail_preview'),
        ]
        return custom_urls + urls

    def send_action(self, obj):
        if obj.status == 'draft':
            return format_html(
                '<a class="button" href="{}">Send Now</a>&nbsp;<a class="button" href="{}">Preview</a>',
                reverse('admin:accounts_customemail_send', args=[obj.pk]),
                reverse('admin:accounts_customemail_preview', args=[obj.pk]),
            )
        elif obj.status == 'sent':
            return format_html('<span style="color: green;">✓ Sent</span>')
        else:
            return obj.status

    send_action.short_description = 'Actions'
    send_action.allow_tags = True

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def send_email_view(self, request, email_id):
        email_obj = get_object_or_404(CustomEmail, pk=email_id)

        if request.method == 'POST':
            if email_obj.status != 'draft':
                messages.error(request, 'This email has already been sent or is not in draft status.')
                return redirect('admin:accounts_customemail_changelist')

            # Get all recipient emails
            recipient_emails = email_obj.get_recipient_emails()

            if not recipient_emails:
                messages.error(request, 'No recipients found. Please add recipients before sending.')
                return redirect('admin:accounts_customemail_change', email_id)

            # Send emails
            successful_sends = 0
            failed_sends = 0

            for recipient_email in recipient_emails:
                try:
                    result = send_custom_email(email_obj, recipient_email)
                    if result:
                        successful_sends += 1
                        # Log successful send
                        CustomEmailLog.objects.create(
                            custom_email=email_obj,
                            recipient_email=recipient_email,
                            status='sent'
                        )
                    else:
                        failed_sends += 1
                        # Log failed send
                        CustomEmailLog.objects.create(
                            custom_email=email_obj,
                            recipient_email=recipient_email,
                            status='failed',
                            error_message='Email send returned 0 (failed)'
                        )
                except Exception as e:
                    failed_sends += 1
                    # Log failed send with error
                    CustomEmailLog.objects.create(
                        custom_email=email_obj,
                        recipient_email=recipient_email,
                        status='failed',
                        error_message=str(e)
                    )

            # Update email object
            email_obj.status = 'sent'
            email_obj.sent_at = timezone.now()
            email_obj.total_recipients = len(recipient_emails)
            email_obj.successful_sends = successful_sends
            email_obj.failed_sends = failed_sends
            email_obj.save()

            messages.success(
                request, 
                f'Email sent! Successfully delivered to {successful_sends} recipients. Failed: {failed_sends}'
            )
            return redirect('admin:accounts_customemail_changelist')

        # GET request - show confirmation page
        recipient_emails = email_obj.get_recipient_emails()
        context = {
            'email_obj': email_obj,
            'recipient_emails': recipient_emails,
            'recipient_count': len(recipient_emails),
        }
        return render(request, 'admin/accounts/customemail/send_confirmation.html', context)

    def preview_email_view(self, request, email_id):
        email_obj = get_object_or_404(CustomEmail, pk=email_id)

        from django.template.loader import render_to_string
        from datetime import datetime

        # Render email preview
        html_content = render_to_string('accounts/email/custom_email.html', {
            'email': email_obj,
            'recipient_email': 'mail@limbsorthopaedic.org',
            'current_year': datetime.now().year,
        })

        context = {
            'email_obj': email_obj,
            'html_content': html_content,
        }
        return render(request, 'admin/accounts/customemail/preview.html', context)