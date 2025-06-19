from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AppointmentForm
from .models import Appointment
from core.models import SocialMedia


class AppointmentCreateView(CreateView):
    """View for booking a new appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment_success')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # If user is logged in, associate appointment with user
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        
        # First save the form to get the appointment instance
        response = super().form_valid(form)
        
        # Send pending confirmation email
        try:
            from accounts.utils import send_appointment_confirmation_email
            send_appointment_confirmation_email(self.object)
            messages.success(self.request, 'Your appointment has been scheduled. Please check your email (ESPECIALLY SPAM FOLDER) for confirmation.')
        except Exception as e:
            print(f"Error sending pending appointment email: {e}")
            messages.success(self.request, 'Your appointment has been scheduled. We will contact you to confirm.')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


class AppointmentSuccessView(TemplateView):
    """View for successful appointment booking"""
    template_name = 'appointments/appointment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
