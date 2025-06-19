
from django.contrib import admin
from django.utils.html import format_html
from .models import Gallery

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.get_image():
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.get_image())
        return "(No image)"
    image_preview.short_description = 'Preview'
