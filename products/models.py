from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class ProductCategory(models.Model):
    """Model for product categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Model for orthopaedic products"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = CKEditor5Field('Description', config_name='extends')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Leave empty if price varies or is available on request")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Optional external URL for image (used if no image is uploaded)")
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', 'title']
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def whatsapp_message(self):
        """Generate a pre-filled WhatsApp message for this product"""
        product_url = f"https://limbsorthopaedic.org{self.get_absolute_url()}"
        return f"Hello *LIMBS Orthopaedic*, I'm interested in {self.title} {product_url}"
    
    @property
    def formatted_price(self):
        """Return formatted price or 'Price on Request' if no price"""
        if self.price:
            return f"KSh {self.price:,.2f}"
        return "Price on Request"
        
    def get_image(self):
        """Return the image (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None


class CustomProductRequest(models.Model):
    """Model for custom product requests from customers"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    details = models.TextField(help_text="Details about the custom product needed")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Custom Product Request from {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Custom Product Request"
        verbose_name_plural = "Custom Product Requests"


class Cart(models.Model):
    """Shopping cart for products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_items(self):
        return self.items.all()


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True, help_text="Special notes or requirements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    def get_total_price(self):
        if self.product.price:
            return self.product.price * self.quantity
        return 0
    
    class Meta:
        unique_together = ('cart', 'product')


class Order(models.Model):
    """Customer orders"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Customer Information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Shipping Information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_notes = models.TextField(blank=True, null=True)
    
    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']
    
    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'order_number': self.order_number})
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def send_status_email(self):
        """Send email notification based on order status"""
        template_mapping = {
            'pending': 'emails/order_placed.html',
            'confirmed': 'emails/order_confirmed.html',
            'shipping': 'emails/order_shipping.html',
            'completed': 'emails/order_completed.html',
        }
        
        subject_mapping = {
            'pending': f'Order Placed #{self.order_number} - LIMBS Orthopaedic',
            'confirmed': f'Order Confirmed #{self.order_number} - LIMBS Orthopaedic',
            'shipping': f'Order Shipped #{self.order_number} - LIMBS Orthopaedic',
            'completed': f'Order Completed #{self.order_number} - LIMBS Orthopaedic',
        }
        
        if self.status in template_mapping:
            context = {
                'order': self,
                'customer_name': self.customer_name,
                'order_items': self.items.all(),
                'company_name': 'LIMBS Orthopaedic',
                'company_email': settings.COMPANY_EMAIL,
                'company_phone': settings.COMPANY_PHONE,
            }
            
            try:
                html_message = render_to_string(template_mapping[self.status], context)
                send_mail(
                    subject=subject_mapping[self.status],
                    message='',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.customer_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending order email: {e}")


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Allow empty price
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} for Order {self.order.order_number}"

    def get_total_price(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return None  # or return "Price on Request"
