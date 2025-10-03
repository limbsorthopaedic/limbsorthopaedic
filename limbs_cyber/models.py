
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class ProductService(models.Model):
    """Model for products and services in the cyber cafe"""
    CATEGORY_CHOICES = (
        ('product', 'Product'),
        ('service', 'Service'),
    )
    
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='product')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0, help_text="Use 999 for unlimited/services")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Product/Service'
        verbose_name_plural = 'Products/Services'
    
    def __str__(self):
        return f"{self.name} - KSh {self.unit_price}"
    
    @property
    def is_in_stock(self):
        return self.current_stock > 0 or self.current_stock == 999
    
    @property
    def stock_status(self):
        if self.current_stock == 999:
            return "Unlimited"
        elif self.current_stock == 0:
            return "Out of Stock"
        elif self.current_stock < 10:
            return f"Low Stock ({self.current_stock})"
        else:
            return f"In Stock ({self.current_stock})"


class Sale(models.Model):
    """Model for recording sales transactions"""
    transaction_number = models.CharField(max_length=50, editable=False)
    product_service = models.ForeignKey(ProductService, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='M-Pesa Pochi (0708581688)')
    notes = models.TextField(blank=True, null=True)
    receipt_generated = models.BooleanField(default=False)
    sale_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Sale Transaction'
        verbose_name_plural = 'Sales Transactions'
    
    def __str__(self):
        return f"{self.transaction_number} - {self.product_service.name} - KSh {self.total_amount}"
    
    def save(self, *args, **kwargs):
        # Generate transaction number
        if not self.transaction_number:
            import uuid
            self.transaction_number = f"CYBER-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate total amount
        self.total_amount = Decimal(str(self.unit_price)) * Decimal(str(self.quantity))
        
        # Update stock on first save
        if not self.pk:
            if self.product_service.current_stock != 999:
                self.product_service.current_stock -= self.quantity
                self.product_service.save()
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_daily_stats(date=None):
        """Get statistics for a specific date"""
        if date is None:
            date = timezone.now().date()
        
        sales = Sale.objects.filter(sale_date__date=date)
        
        return {
            'total_sales': sales.count(),
            'total_revenue': sum(sale.total_amount for sale in sales),
            'total_items': sum(sale.quantity for sale in sales),
            'sales': sales
        }
    
    @staticmethod
    def get_period_stats(start_date, end_date):
        """Get statistics for a date range"""
        sales = Sale.objects.filter(sale_date__date__range=[start_date, end_date])
        
        return {
            'total_sales': sales.count(),
            'total_revenue': sum(sale.total_amount for sale in sales),
            'total_items': sum(sale.quantity for sale in sales),
            'sales': sales
        }


class DailySummary(models.Model):
    """Model for daily summary reports"""
    date = models.DateField(unique=True)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Daily Summary'
        verbose_name_plural = 'Daily Summaries'
    
    def __str__(self):
        return f"Summary for {self.date} - KSh {self.total_revenue}"
    
    @classmethod
    def generate_for_date(cls, date):
        """Generate or update daily summary for a specific date"""
        stats = Sale.get_daily_stats(date)
        
        summary, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_sales': stats['total_sales'],
                'total_revenue': stats['total_revenue'],
                'total_items_sold': stats['total_items'],
            }
        )
        return summary
