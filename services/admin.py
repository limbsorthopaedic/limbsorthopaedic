from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, Service, ServiceImage


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'image_url', 'title', 'description', 'order', 'is_active', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.get_image():
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.get_image())
        return "(No image)"
    
    image_preview.short_description = 'Preview'


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'order', 'is_active', 'image_preview')
    list_filter = ('service', 'is_active')
    search_fields = ('title', 'description', 'service__title')
    ordering = ('service', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.get_image():
            return format_html('<img src="{}" style="max-height: 150px; max-width: 150px;" />', obj.get_image())
        return "(No image)"
    
    image_preview.short_description = 'Preview'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'featured', 'is_active', 'order', 'image_count')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'featured', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    inlines = [ServiceImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Display Options', {
            'fields': ('image', 'image_url', 'icon_class', 'featured', 'order', 'is_active'),
            'description': 'Note: The legacy image fields will only be used if no Service Images are defined.'
        }),
    )
    
    def image_count(self, obj):
        count = obj.service_images.count()
        return count
    
    image_count.short_description = 'Images'
