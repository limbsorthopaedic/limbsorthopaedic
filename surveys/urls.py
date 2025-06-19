from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Survey list and detail views
    path('', views.survey_list, name='survey_list'),
    path('<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('<int:survey_id>/update/', views.update_survey, name='update_survey'),
    path('<int:survey_id>/start/', views.start_survey, name='start_survey'),
    path('<int:survey_id>/submit/', views.submit_survey, name='submit_survey'),
    path('<int:survey_id>/thanks/', views.thank_you, name='thank_you'),

    # AJAX endpoints
    path('api/questions/<int:survey_id>/', views.get_survey_questions, name='get_survey_questions'),
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),

    # For appointment-related surveys
    path('appointment/<int:appointment_id>/', views.appointment_survey, name='appointment_survey'),
]