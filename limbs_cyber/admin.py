from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import ProductService, Sale, DailySummary


@admin.register(ProductService)
class ProductServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_price', 'current_stock', 'stock_status', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('unit_price', 'current_stock', 'is_active')
    ordering = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('unit_price', 'current_stock'),
            'description': 'Use 999 for unlimited stock (services) or 0 for out of stock'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def stock_status(self, obj):
        status = obj.stock_status
        if 'Out of Stock' in status:
            color = 'red'
        elif 'Low Stock' in status:
            color = 'orange'
        elif 'Unlimited' in status:
            color = 'green'
        else:
            color = 'blue'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, status)

    stock_status.short_description = 'Stock Status'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('transaction_number', 'product_service', 'quantity', 'total_amount', 'customer_name', 'staff', 'sale_date', 'receipt_generated')
    list_filter = ('sale_date', 'product_service', 'staff', 'receipt_generated')
    search_fields = ('transaction_number', 'customer_name', 'notes')
    readonly_fields = ('transaction_number', 'total_amount', 'created_at', 'sale_date')
    date_hierarchy = 'sale_date'
    ordering = ('-sale_date',)

    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_number', 'sale_date', 'product_service', 'quantity', 'unit_price', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'payment_method', 'notes')
        }),
        ('Staff & Receipt', {
            'fields': ('staff', 'receipt_generated')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent manual addition through admin (use POS interface)
        return False


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_revenue', 'total_items_sold')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_sales', 'total_revenue', 'total_items_sold', 'created_at', 'updated_at')
    ordering = ('-date',)

    fieldsets = (
        ('Summary for Date', {
            'fields': ('date', 'total_sales', 'total_revenue', 'total_items_sold')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Summaries are auto-generated
        return False