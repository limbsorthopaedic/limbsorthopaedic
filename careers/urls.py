from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    path('', views.career_list, name='career_list'),
    path('job-application/<int:career_id>/', views.job_application, name='job_application'),
    path('submit/', views.submit_application, name='submit_application'),
    path('success/', views.career_success, name='success'),
]