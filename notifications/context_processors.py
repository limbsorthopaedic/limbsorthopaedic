from .models import get_unread_count, get_unread_by_category

def unread_notifications(request):
    """
    Context processor that adds notification counts to context
    """
    # Only add notification data for staff users
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'unread_notifications_count': get_unread_count(),
            'notification_counts_by_category': {
                str(c['id']): c['unread_count'] 
                for c in get_unread_by_category()
            }
        }
    
    return {
        'unread_notifications_count': 0,
        'notification_counts_by_category': {}
    }