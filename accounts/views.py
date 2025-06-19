from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Count
from .forms import SignUpForm, ProfileForm, UserUpdateForm
from .models import Profile, Doctor
from .utils import send_welcome_email, send_password_reset_email
from appointments.models import Appointment
from core.models import SocialMedia
from surveys.models import Survey, Response


class SignUpView(CreateView):
    """View for user registration"""
    form_class = SignUpForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        # Save the user
        response = super().form_valid(form)
        
        # Create a profile for the user
        phone_number = form.cleaned_data.get('phone_number')
        Profile.objects.create(user=self.object, phone_number=phone_number)
        
        # Send welcome email
        try:
            send_welcome_email(self.object)
            messages.success(self.request, 'Account created successfully. A welcome email has been sent to your email address.')
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Error sending welcome email: {e}")
            messages.success(self.request, 'Account created successfully. You can now log in.')
        
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating user profile"""
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        # Get or create profile for the user
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_form_class(self):
        return ProfileForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        context['appointments'] = Appointment.objects.filter(user=self.request.user).order_by('-preferred_date')
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        
        # Get user's orders and products
        from products.models import Order
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Get active surveys with question counts
        context['available_surveys'] = Survey.objects.filter(is_active=True).annotate(
            question_count=Count('questions')
        )
        
        # Get user's completed surveys
        context['completed_survey_ids'] = Response.objects.filter(
            user=self.request.user,
            is_complete=True
        ).values_list('survey_id', flat=True)
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = self.get_form()
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if 'update_user' in request.POST:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Basic information updated successfully.')
                return redirect('profile')
            else:
                return self.render_to_response(self.get_context_data(form=self.get_form(), user_form=user_form))
        
        elif 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Profile information updated successfully.')
                return redirect('profile')
            else:
                return self.render_to_response(self.get_context_data(form=profile_form, user_form=UserUpdateForm(instance=request.user)))
        
        return self.render_to_response(self.get_context_data(form=profile_form, user_form=user_form))


class IsDoctorMixin(UserPassesTestMixin):
    """Mixin to ensure user is a doctor"""
    def test_func(self):
        return hasattr(self.request.user, 'doctor')
        
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('home')


class DoctorDashboardView(LoginRequiredMixin, IsDoctorMixin, TemplateView):
    """View for doctor dashboard"""
    template_name = 'accounts/doctor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the doctor instance
        doctor = self.request.user.doctor
        context['doctor'] = doctor
        
        # Get all appointments assigned to this doctor
        context['appointments'] = Appointment.objects.filter(user__isnull=False).order_by('-preferred_date')
        
        # Group appointments by status
        context['upcoming_appointments'] = context['appointments'].filter(status__in=['pending', 'confirmed'])
        context['completed_appointments'] = context['appointments'].filter(status='completed')
        
        # Get social media links for footer
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        
        return context


class DoctorProfileUpdateView(LoginRequiredMixin, IsDoctorMixin, UpdateView):
    """View for updating doctor profile"""
    model = Doctor
    template_name = 'accounts/doctor_profile.html'
    fields = ['gender', 'specialty', 'profile_image', 'profile_image_url', 'office_location']
    success_url = reverse_lazy('doctor_dashboard')
    
    def get_object(self):
        # Return the doctor instance for the current user
        return self.request.user.doctor
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserUpdateForm(instance=self.request.user)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Get current doctor instance
        doctor_form = self.get_form()
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if doctor_form.is_valid() and user_form.is_valid():
            with transaction.atomic():
                user_form.save()
                doctor = doctor_form.save(commit=False)
                doctor.user = request.user  # Ensure user association
                doctor.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('doctor_dashboard')
        else:
            return self.render_to_response(self.get_context_data(form=doctor_form, user_form=user_form))


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view that uses our own email function"""
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        """Send a custom reset email instead of the Django default one"""
        # Get the user email
        email = form.cleaned_data["email"]
        
        # Debug log
        print(f"Password reset requested for email: {email}")
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        print(f"Email host: {settings.EMAIL_HOST}")
        print(f"Email port: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        
        # Find users with this email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        
        # Check if we found any users
        if not active_users.exists():
            print(f"No active users found with email: {email}")
            # We still return success to avoid leaking information about which emails are registered
            return super().form_valid(form)
        
        print(f"Found {active_users.count()} active users with email: {email}")
        
        # Send reset email to each user
        for user in active_users:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            try:
                # Use our custom email sending function
                result = send_password_reset_email(user, token, uid)
                print(f"Password reset email sent to {user.email} - Result: {result}")
                
                # Add a success message for the user
                messages.success(self.request, f"Password reset email sent to {email}. Please check your inbox.")
            except Exception as e:
                print(f"Error sending password reset email: {e}")
                print(f"Error type: {type(e).__name__}")
                
                # Log the error but don't show it to the user
                # Instead, provide a helpful message
                messages.warning(
                    self.request, 
                    "There was an issue sending the password reset email. "
                    "Please try again later or contact support if the problem persists."
                )
        
        # Return the success response
        return super().form_valid(form)
