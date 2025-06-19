from django.contrib import admin
from .models import PageSection, SiteSetting


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'section_type', 'is_active', 'order', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('identifier', 'title', 'subtitle', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'order')
    
    fieldsets = (
        ('Identification', {
            'fields': ('identifier', 'section_type', 'is_active', 'order')
        }),
        ('Content', {
            'fields': ('title', 'subtitle', 'content')
        }),
        ('Images', {
            'fields': ('image', 'image_url')
        }),
        ('Button', {
            'fields': ('button_text', 'button_url'),
            'classes': ('collapse',),
        }),
        ('Styling', {
            'fields': ('custom_css_class',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Clear the site settings cache when a section is updated
        """
        from django.core.cache import cache
        cache.delete('site_settings')
        super().save_model(request, obj, form, change)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'truncated_value', 'is_public', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_public',)
    
    fieldsets = (
        ('Setting', {
            'fields': ('key', 'value', 'description', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def truncated_value(self, obj):
        """Return a truncated version of the value field for display in the list view"""
        if len(obj.value) > 50:
            return f"{obj.value[:50]}..."
        return obj.value
    
    truncated_value.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        """
        Clear the site settings cache when a setting is updated
        """
        from django.core.cache import cache
        cache.delete('site_settings')
        super().save_model(request, obj, form, change)