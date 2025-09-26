"""
Admin site configuration for LIMBS Orthopaedic project.
This file configures both the primary and secondary admin sites.
"""

from django.contrib import admin
from django.apps import apps
from .models import Invoice, InvoiceItem


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'patient_name', 'tracking_code']
    readonly_fields = ['invoice_number', 'tracking_code', 'created_by', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new invoice
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'total_price']
    list_filter = ['invoice__status']
    search_fields = ['description', 'invoice__invoice_number']


# Create function to register models that can be called after secondary_admin_site is created
def register_models_to_secondary_admin(secondary_admin_site):
    # Get all models from installed apps
    app_models = {}
    for app_config in apps.get_app_configs():
        app_label = app_config.label
        if app_label not in ['admin', 'contenttypes', 'sessions', 'auth', 'messages', 'staticfiles']:
            for model in app_config.get_models():
                app_models[model] = app_label

    # Register all models from our apps to secondary admin site
    for model, app_label in app_models.items():
        try:
            # Get the ModelAdmin class that Django admin is using (if it exists)
            model_admin = type(admin.site._registry.get(model, admin.ModelAdmin))

            # Check if the model is already registered with the main admin site
            if model in admin.site._registry:
                # Register the same model with the secondary admin site
                secondary_admin_site.register(model, model_admin)
        except Exception as e:
            # Just log the error but continue with other models
            print(f"Error registering {model.__name__} to secondary admin site: {e}")