from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'rating', 'is_featured', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_featured', 'is_approved')
    search_fields = ('name', 'title', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_featured', 'is_approved')
    
    actions = ['approve_testimonials', 'feature_testimonials', 'unfeature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} testimonials have been approved.')
    approve_testimonials.short_description = "Approve selected testimonials"
    
    def feature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials have been featured.')
    feature_testimonials.short_description = "Feature selected testimonials"
    
    def unfeature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} testimonials have been unfeatured.')
    unfeature_testimonials.short_description = "Unfeature selected testimonials"
