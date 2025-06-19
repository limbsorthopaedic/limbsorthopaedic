from django.db import models
from django.contrib.auth.models import User
from services.models import Service
from accounts.models import Doctor


class Appointment(models.Model):
    """Model for appointment bookings"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # If user is logged in, link to their account, otherwise store contact information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    
    # Contact information
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Appointment details
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    other_service = models.CharField(max_length=200, blank=True, null=True, help_text="If service not listed above")
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    notes = models.TextField(blank=True, null=True, help_text="Any additional information or special requirements")
    
    # Status information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin notes (not visible to patients)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes for admin purposes only")
    
    # Doctor assignment
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='assigned_appointments',
                                       help_text="Doctor assigned to this appointment")
    
    # Treatment notes and history
    treatment_notes = models.TextField(blank=True, null=True, 
                                     help_text="Detailed notes about patient's treatment")
    treatment_date = models.DateField(null=True, blank=True, 
                                    help_text="Date when treatment was provided")
    follow_up_date = models.DateField(null=True, blank=True, 
                                    help_text="Date for follow-up appointment if needed")
    
    def __str__(self):
        return f"{self.full_name} - {self.preferred_date} {self.preferred_time}"
    
    class Meta:
        ordering = ['-preferred_date', '-preferred_time']
