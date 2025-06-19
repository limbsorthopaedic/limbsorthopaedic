from django.contrib import admin
from django.utils import timezone
from .models import ProductCategory, Product, CustomProductRequest, Cart, CartItem, Order, OrderItem


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'formatted_price', 'featured', 'is_active', 'order')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'featured', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'category', 'price')
        }),
        ('Display Options', {
            'fields': ('image', 'image_url', 'featured', 'order', 'is_active')
        }),
    )
    
    def formatted_price(self, obj):
        return obj.formatted_price
    formatted_price.short_description = 'Price'


@admin.register(CustomProductRequest)
class CustomProductRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'phone', 'details')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Request Details', {
            'fields': ('details', 'created_at')
        }),
        ('Processing', {
            'fields': ('is_processed', 'admin_notes')
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'customer_email', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'confirmed_at', 'shipped_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_notes')
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            old_status = old_obj.status
        
        super().save_model(request, obj, form, change)
        
        # Send email if status changed
        if old_status and old_status != obj.status:
            # Update timestamp fields based on status
            if obj.status == 'confirmed' and not obj.confirmed_at:
                obj.confirmed_at = timezone.now()
                obj.save()
            elif obj.status == 'shipping' and not obj.shipped_at:
                obj.shipped_at = timezone.now()
                obj.save()
            elif obj.status == 'delivered' and not obj.delivered_at:
                obj.delivered_at = timezone.now()
                obj.save()
            
            obj.send_status_email()
