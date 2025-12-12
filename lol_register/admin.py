from django.contrib import admin
from .models import LOLProductService


@admin.register(LOLProductService)
class LOLProductServiceAdmin(admin.ModelAdmin):
    """Admin interface for LOL Products & Services - the only model in Django Admin"""
    list_display = ['name', 'price', 'active', 'created_at', 'updated_at']
    list_filter = ['active']
    search_fields = ['name']
    list_editable = ['price', 'active']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'active')
        }),
    )
