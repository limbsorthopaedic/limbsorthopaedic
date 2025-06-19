from django.contrib import admin
from django.contrib import messages
from .models import Appointment
from accounts.utils import send_appointment_confirmation_email


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'service_name', 'preferred_date', 'assigned_doctor_name', 'status', 'created_at')
    list_filter = ('status', 'preferred_date', 'assigned_doctor')
    search_fields = ('full_name', 'email', 'phone', 'notes', 'treatment_notes')
    ordering = ['-preferred_date', '-preferred_time']
    date_hierarchy = 'preferred_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('service', 'other_service', 'preferred_date', 'preferred_time', 'notes')
        }),
        ('Doctor Assignment', {
            'fields': ('assigned_doctor',),
            'description': 'Assign a doctor to handle this appointment'
        }),
        ('Treatment Records', {
            'fields': ('treatment_notes', 'treatment_date', 'follow_up_date'),
            'classes': ('collapse',),
            'description': 'Treatment details and follow-up information'
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
    )
    
    def service_name(self, obj):
        if obj.service:
            return obj.service.title
        elif obj.other_service:
            return f"Other: {obj.other_service}"
        return "Not specified"
    service_name.short_description = 'Service'
    
    def assigned_doctor_name(self, obj):
        if obj.assigned_doctor:
            return f"{obj.assigned_doctor.user.get_full_name()} ({obj.assigned_doctor.specialty})"
        return "Not assigned"
    assigned_doctor_name.short_description = 'Doctor'
    
    def save_model(self, request, obj, form, change):
        """
        When an appointment status is changed:
        1. Update treatment date if status is 'completed'
        2. Send email notification if status is 'confirmed'
        """
        is_status_changed = change and 'status' in form.changed_data
        is_newly_confirmed = is_status_changed and obj.status == 'confirmed'
        
        # If status is changed to completed and there's no treatment date yet,
        # set the treatment date to today
        if is_status_changed and obj.status == 'completed' and not obj.treatment_date:
            from datetime import date
            obj.treatment_date = date.today()
        
        # Save the appointment
        super().save_model(request, obj, form, change)
        
        # Send email for any status change
        if is_status_changed:
            try:
                email_sent = send_appointment_confirmation_email(obj)
                if email_sent:
                    messages.success(request, f"Status update email sent to {obj.email}")
                else:
                    messages.warning(request, f"Failed to send status update email to {obj.email}")
            except Exception as e:
                messages.error(request, f"Error sending email: {str(e)}")
                messages.error(request, f"Error sending confirmation email: {str(e)}")
                # Log the error but don't raise it
                print(f"Error sending appointment confirmation email: {e}")
