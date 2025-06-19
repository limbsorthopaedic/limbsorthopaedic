from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """Form for booking an appointment"""
    
    # Override preferred_date to use DateInput widget with HTML5 date input
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400'}),
        help_text="Please select a date (must be at least tomorrow)"
    )
    
    # Override preferred_time to use TimeInput widget with HTML5 time input
    preferred_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400'}),
        help_text="Please select a time between 8:00 AM and 5:00 PM"
    )
    
    class Meta:
        model = Appointment
        fields = ['full_name', 'email', 'phone', 'service', 'other_service', 'preferred_date', 'preferred_time', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Your Phone Number'}),
            'service': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400'}),
            'other_service': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Specify service if not listed above'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Any additional information or special requirements', 'rows': 4}),
        }
    
    def clean_preferred_date(self):
        """Validate that the date is not in the past and not today"""
        date = self.cleaned_data.get('preferred_date')
        today = timezone.now().date()
        
        if date <= today:
            raise forms.ValidationError("Appointment date must be at least tomorrow.")
        
        return date
    
    def clean_preferred_time(self):
        """Validate that the time is within business hours (8 AM to 5 PM)"""
        time = self.cleaned_data.get('preferred_time')
        
        if time:
            # Check that time is between 8 AM and 5 PM
            if time.hour < 8 or time.hour >= 17:
                raise forms.ValidationError("Appointments are only available between 8:00 AM and 5:00 PM.")
        
        return time
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is authenticated, pre-fill the form with their information
        if user and user.is_authenticated:
            self.fields['full_name'].initial = f"{user.first_name} {user.last_name}".strip()
            self.fields['email'].initial = user.email
