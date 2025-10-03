
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from django.utils import timezone
from .models import ProductService, Sale, DailySummary


@admin.register(ProductService)
class ProductServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'formatted_price', 'stock_display', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('unit_price', 'current_stock')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def formatted_price(self, obj):
        return f"KSh {obj.unit_price:,.2f}"
    formatted_price.short_description = 'Unit Price'
    
    def stock_display(self, obj):
        status = obj.stock_status
        if 'Out of Stock' in status:
            color = 'red'
        elif 'Low Stock' in status:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, status)
    stock_display.short_description = 'Stock Status'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('transaction_number', 'product_service', 'quantity', 'formatted_total', 'customer_name', 'staff', 'sale_date', 'receipt_generated')
    list_filter = ('sale_date', 'product_service', 'staff', 'receipt_generated')
    search_fields = ('transaction_number', 'customer_name', 'product_service__name')
    readonly_fields = ('transaction_number', 'total_amount', 'created_at')
    date_hierarchy = 'sale_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_number', 'product_service', 'quantity', 'unit_price', 'total_amount')
        }),
        ('Customer & Staff', {
            'fields': ('customer_name', 'staff')
        }),
        ('Payment', {
            'fields': ('payment_method', 'receipt_generated')
        }),
        ('Additional Information', {
            'fields': ('notes', 'sale_date', 'created_at')
        }),
    )
    
    def formatted_total(self, obj):
        return f"KSh {obj.total_amount:,.2f}"
    formatted_total.short_description = 'Total Amount'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.staff = request.user
            if not obj.unit_price:
                obj.unit_price = obj.product_service.unit_price
        super().save_model(request, obj, form, change)


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'formatted_revenue', 'total_items_sold', 'view_details')
    list_filter = ('date',)
    readonly_fields = ('total_sales', 'total_revenue', 'total_items_sold', 'created_at', 'updated_at')
    date_hierarchy = 'date'
    
    def formatted_revenue(self, obj):
        return f"KSh {obj.total_revenue:,.2f}"
    formatted_revenue.short_description = 'Total Revenue'
    
    def view_details(self, obj):
        url = reverse('cyber_daily_report', kwargs={'date': obj.date.strftime('%Y-%m-%d')})
        return format_html('<a class="button" href="{}" target="_blank">View Report</a>', url)
    view_details.short_description = 'Actions'
