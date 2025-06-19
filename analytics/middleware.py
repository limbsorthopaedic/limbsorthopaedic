
from django.utils import timezone
from django.conf import settings
from .models import PageVisit

class VisitTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            # Get or set visitor cookie
            visitor_id = request.COOKIES.get('visitor_id', None)
            
            PageVisit.objects.create(
                path=request.path,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                visitor_id=visitor_id
            )

        response = self.get_response(request)
        
        # Set visitor cookie if it doesn't exist
        if not request.COOKIES.get('visitor_id'):
            import uuid
            visitor_id = str(uuid.uuid4())
            response.set_cookie('visitor_id', visitor_id, max_age=365*24*60*60)  # 1 year
            
        return response
