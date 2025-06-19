from django.urls import path
from .views import AppointmentCreateView, AppointmentSuccessView

urlpatterns = [
    path('create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('', AppointmentCreateView.as_view(), name='appointment'),  # Add this line
    path('success/', AppointmentSuccessView.as_view(), name='appointment_success'),
]
# urlpatterns = [
#     path('', AppointmentCreateView.as_view(), name='appointment'),
#     path('success/', AppointmentSuccessView.as_view(), name='appointment_success'),
# ]
