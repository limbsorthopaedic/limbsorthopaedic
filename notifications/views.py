from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.contrib import admin

from .models import Notification, get_unread_count, mark_all_as_read


def is_staff(user):
    """Check if user is staff"""
    return user.is_staff


@login_required
@user_passes_test(is_staff)
@csrf_protect
@require_POST
def mark_read(request):
    """Mark a notification as read"""
    notification_id = request.POST.get('notification_id')
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)


@login_required
@user_passes_test(is_staff)
@csrf_protect
@require_POST
def mark_all_read(request):
    """Mark all notifications as read"""
    count = mark_all_as_read()
    
    return JsonResponse({
        'success': True,
        'marked_count': count,
        'unread_count': 0  # Should be 0 after marking all as read
    })


@login_required
@user_passes_test(is_staff)
def unread_notifications(request):
    """Redirect to notifications list with unread filter"""
    url = reverse('admin:notifications_notification_changelist') + '?is_read__exact=0'
    return HttpResponseRedirect(url)