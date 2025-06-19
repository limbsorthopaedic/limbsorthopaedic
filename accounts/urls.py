from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SignUpView, 
    ProfileUpdateView,
    DoctorDashboardView,
    DoctorProfileUpdateView,
    CustomPasswordResetView
)
from .forms import CustomLoginForm

urlpatterns = [
    # Authentication views
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=CustomLoginForm,
        redirect_authenticated_user=True,
        next_page='profile'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/',
        template_name=None
    ), name='logout'),
    
    # Registration view
    path('register/', SignUpView.as_view(), name='register'),
    
    # Password reset views - using our custom view
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Profile view
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    
    # Doctor views
    path('doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('doctor/profile/', DoctorProfileUpdateView.as_view(), name='doctor_profile'),
]
