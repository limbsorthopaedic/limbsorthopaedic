
from django.db import models
from django.utils import timezone

class PageVisit(models.Model):
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    visitor_id = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    @classmethod
    def get_visit_counts(cls):
        today = timezone.now().date()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        return {
            'today': cls.objects.filter(timestamp__date=today).count(),
            'month': cls.objects.filter(timestamp__gte=month_start).count(),
            'year': cls.objects.filter(timestamp__gte=year_start).count(),
            'all_time': cls.objects.count(),
        }
