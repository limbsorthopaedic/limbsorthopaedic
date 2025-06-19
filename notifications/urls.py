from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('admin/notifications/mark-read/', views.mark_read, name='mark_read'),
    path('admin/notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('admin/notifications/unread/', views.unread_notifications, name='unread_notifications'),
]