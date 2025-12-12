from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
import string


class LOLProductService(models.Model):
    """Products and Services for Limbs Orthopaedic Clinic - Admin managed only"""
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'LOL - Products & Services List'
        verbose_name_plural = 'LOL - Products & Services List'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - KSh {self.price:,.2f}"


class Patient(models.Model):
    """Patient registration model"""
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    
    CATEGORY_CHOICES = (
        ('Child', 'Child'),
        ('Adult', 'Adult'),
    )
    
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age_years = models.PositiveIntegerField(default=0)
    age_months = models.PositiveIntegerField(default=0)
    child_or_adult = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    brought_by = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=20)
    alt_contact = models.CharField(max_length=20, blank=True, null=True)
    residence = models.CharField(max_length=255)
    info_source = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="How did you hear about us?"
    )
    unique_code = models.CharField(max_length=10, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.full_name} ({self.unique_code})"

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        """Generate unique code in LOL-XXXXX format"""
        while True:
            code = 'LOL-' + ''.join(random.choices(string.digits, k=5))
            if not Patient.objects.filter(unique_code=code).exists():
                return code


class Visit(models.Model):
    """Patient visit record with snapshot of patient data"""
    VISIT_STATUS_CHOICES = (
        ('New', 'New'),
        ('Old', 'Old'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='visits')
    visit_status = models.CharField(max_length=10, choices=VISIT_STATUS_CHOICES, default='New')
    
    # Snapshot fields - duplicate patient data at time of visit
    snapshot_full_name = models.CharField(max_length=255)
    snapshot_gender = models.CharField(max_length=10)
    snapshot_age_years = models.PositiveIntegerField(default=0)
    snapshot_age_months = models.PositiveIntegerField(default=0)
    snapshot_child_or_adult = models.CharField(max_length=10)
    snapshot_brought_by = models.CharField(max_length=255, blank=True, null=True)
    snapshot_contact = models.CharField(max_length=20)
    snapshot_alt_contact = models.CharField(max_length=20, blank=True, null=True)
    snapshot_residence = models.CharField(max_length=255)
    snapshot_info_source = models.CharField(max_length=255, blank=True, null=True)
    
    # Clinical data
    diagnosis = models.TextField(blank=True, null=True)
    treatment_notes = models.TextField(blank=True, null=True)
    next_visit = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'

    def __str__(self):
        return f"Visit - {self.patient.unique_code} on {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        # Auto-populate snapshot fields from patient if this is a new visit
        if not self.pk:
            self.snapshot_full_name = self.patient.full_name
            self.snapshot_gender = self.patient.gender
            self.snapshot_age_years = self.patient.age_years
            self.snapshot_age_months = self.patient.age_months
            self.snapshot_child_or_adult = self.patient.child_or_adult
            self.snapshot_brought_by = self.patient.brought_by
            self.snapshot_contact = self.patient.contact
            self.snapshot_alt_contact = self.patient.alt_contact
            self.snapshot_residence = self.patient.residence
            self.snapshot_info_source = self.patient.info_source
            
            # Determine visit status based on previous visits
            if self.patient.visits.exists():
                self.visit_status = 'Old'
            else:
                self.visit_status = 'New'
        
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        """Calculate total amount for this visit"""
        total = sum(vp.subtotal for vp in self.visit_products.exclude(status='Cancelled'))
        return total

    @property
    def total_paid(self):
        """Calculate total paid for this visit"""
        total = sum(p.amount_paid or Decimal('0') for p in self.payments.all())
        return total

    @property
    def outstanding_balance(self):
        """Calculate outstanding balance"""
        return self.total_amount - self.total_paid


class VisitProduct(models.Model):
    """Products/Services linked to a visit"""
    STATUS_CHOICES = (
        ('To Make', 'To Make'),
        ('Made/Fitted', 'Made/Fitted'),
        ('Repaired', 'Repaired'),
        ('Cancelled', 'Cancelled'),
    )
    
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='visit_products')
    product = models.ForeignKey(LOLProductService, on_delete=models.PROTECT)
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Make')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Visit Product'
        verbose_name_plural = 'Visit Products'

    def __str__(self):
        return f"{self.product.name} x{self.quantity} for {self.visit.patient.unique_code}"

    def save(self, *args, **kwargs):
        # Set price at time of adding if not set
        if not self.price_at_time:
            self.price_at_time = self.product.price
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.price_at_time * self.quantity


class WorkshopOrder(models.Model):
    """Workshop/Manufacturing orders"""
    STATUS_CHOICES = (
        ('To Make', 'To Make'),
        ('In Progress', 'In Progress'),
        ('Made', 'Made'),
        ('Fitted', 'Fitted'),
        ('Repaired', 'Repaired'),
    )
    
    visit_product = models.OneToOneField(
        VisitProduct, 
        on_delete=models.CASCADE, 
        related_name='workshop_order'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Make')
    expected_ready_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_workshop_orders'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workshop Order'
        verbose_name_plural = 'Workshop Orders'

    def __str__(self):
        return f"Order: {self.visit_product.product.name} - {self.status}"


class LOLPayment(models.Model):
    """Payment/Cash Book records"""
    PAYMENT_METHOD_CHOICES = (
        ('LOL-MPESA', 'LOL-MPESA'),
        ('LOL-CASH', 'LOL-CASH'),
    )
    
    visit = models.ForeignKey(Visit, on_delete=models.PROTECT, related_name='payments')
    visit_product = models.ForeignKey(
        VisitProduct, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payments'
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    expected_pay = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)
    paid_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'LOL Payment'
        verbose_name_plural = 'LOL Payments (Cash Book)'

    def __str__(self):
        return f"Payment: {self.visit.patient.unique_code} - KSh {self.amount_paid or 0:,.2f}"

    def save(self, *args, **kwargs):
        # Auto-calculate balance
        paid = self.amount_paid or Decimal('0')
        self.balance = self.expected_pay - paid
        super().save(*args, **kwargs)
