"""
URL configuration for limbs_orthopaedic project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.admin import AdminSite
from .admin_views import (
    admin_dashboard, admin_logout_view, admin_invoice_generator,
    admin_invoice_list, admin_invoice_detail, admin_invoice_edit,
    admin_save_invoice, admin_invoice_delete
)
from core import views as core_views

from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from django.contrib.sitemaps import GenericSitemap
from products.models import Product

# Create a custom admin site for the secondary URL
class SecondaryAdminSite(AdminSite):
    site_header = 'LIMBS Orthopaedic Administration'
    site_title = 'LIMBS Orthopaedic Admin Portal'
    index_title = 'Welcome to LIMBS Orthopaedic Admin Portal'

# Initialize the secondary admin site
secondary_admin_site = SecondaryAdminSite(name='secondary_admin')

# Import and run the registration function from admin.py
from limbs_orthopaedic.admin import register_models_to_secondary_admin
register_models_to_secondary_admin(secondary_admin_site)

# Product sitemap info
product_dict = {
    'queryset': Product.objects.all(),
    'date_field': 'updated_at',
}

sitemaps = {
    'products': GenericSitemap(product_dict, priority=0.9),
}

urlpatterns = [
    # Use only adminlimbsorth as the primary admin URL
    path('adminlimbsorth/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('adminlimbsorth/invoice-generator/', admin_invoice_generator, name='admin_invoice_generator'),
    path('adminlimbsorth/invoices/', admin_invoice_list, name='admin_invoice_list'),
    path('adminlimbsorth/invoices/<int:invoice_id>/', admin_invoice_detail, name='admin_invoice_detail'),
    path('adminlimbsorth/invoices/<int:invoice_id>/edit/', admin_invoice_edit, name='admin_invoice_edit'),
    path('adminlimbsorth/invoices/<int:invoice_id>/delete/', admin_invoice_delete, name='admin_invoice_delete'),
    path('adminlimbsorth/save-invoice/', admin_save_invoice, name='admin_save_invoice'),
    path('adminlimbsorth/logout/', admin_logout_view, name='admin_logout'),
    path('adminlimbsorth/', admin.site.urls),  # Primary admin URL
    path('set-theme/', core_views.set_theme_preference, name='set_theme'),
    path('get-theme/', core_views.get_theme_preference, name='get_theme'),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('products/', include('products.urls')),
    path('appointments/', include('appointments.urls')),
    path('blog/', include('blog.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('content/', include('content_manager.urls')),
    path('', include('chatbot.urls')),
    path('accounts/', include('accounts.urls')),
    # CKEditor 5 URLs
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('', include('notifications.urls')),
    path('surveys/', include('surveys.urls')),
    path('staff-chat/', include('staff_chat.urls')),
    path('gallery/', include('gallery.urls')),
    path('careers/', include('careers.urls', namespace='careers')),

    # ...existing code...
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", 
         content_type="text/plain")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add static and media URLs (for both development and production in this case)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = 'LIMBS Orthopaedic Administration'
admin.site.site_title = 'LIMBS Orthopaedic Admin Portal'
admin.site.index_title = 'Welcome to LIMBS Orthopaedic Admin Portal'

# Import error handlers (this makes them available to Django)
from limbs_orthopaedic.views import handler404, handler403, handler500

# Configure handlers for production
handler404 = 'limbs_orthopaedic.views.handler404'
handler403 = 'limbs_orthopaedic.views.handler403'
handler500 = 'limbs_orthopaedic.views.handler500'