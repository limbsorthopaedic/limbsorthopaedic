
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import json


class Invoice(models.Model):
    """Model to store invoice data"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    tracking_code = models.CharField(max_length=50, unique=True)
    
    # Patient Information
    patient_name = models.CharField(max_length=200)
    patient_address = models.TextField()
    patient_phone = models.CharField(max_length=20)
    
    # Invoice Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'limbs_orthopaedic'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient_name}"
    
    def get_absolute_url(self):
        return reverse('admin_invoice_detail', kwargs={'invoice_id': self.id})


class InvoiceItem(models.Model):
    """Model to store invoice line items"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        app_label = 'limbs_orthopaedic'
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x KSh {self.unit_price}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
