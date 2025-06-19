
from django.contrib import admin
from .models import Career, CareerApplication

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'job_type', 'location')
    search_fields = ('title', 'about', 'requirements')

@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'career', 'email', 'status', 'created_at')
    list_filter = ('status', 'career', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status == 'accepted':
                # Send job offer email
                obj.send_job_offer_email()
            elif obj.status == 'rejected':
                # Send rejection email
                obj.send_rejection_email()
        super().save_model(request, obj, form, change)
