from django.urls import path
from . import views

app_name = 'staff_chat'

urlpatterns = [
    path('', views.staff_chat, name='staff_chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-new-messages/', views.get_new_messages, name='get_new_messages'),
    path('download-attachment/<int:attachment_id>/', views.download_attachment, name='download_attachment'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('edit-message/<int:message_id>/', views.edit_message, name='edit_message'),
]