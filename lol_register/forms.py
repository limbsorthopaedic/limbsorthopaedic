from django import forms
from django.contrib.auth.models import User
from .models import Patient, Visit, VisitProduct, WorkshopOrder, LOLPayment, LOLProductService


class PatientForm(forms.ModelForm):
    """Form for creating and updating patients"""
    
    class Meta:
        model = Patient
        fields = [
            'full_name', 'gender', 'age_years', 'age_months', 
            'child_or_adult', 'brought_by', 'contact', 'alt_contact',
            'residence', 'info_source'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'age_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Years'
            }),
            'age_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 11,
                'placeholder': 'Months'
            }),
            'child_or_adult': forms.Select(attrs={
                'class': 'form-select'
            }),
            'brought_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of person who brought patient'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary phone number'
            }),
            'alt_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative phone number (optional)'
            }),
            'residence': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter residence/address'
            }),
            'info_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How did you hear about us?'
            }),
        }


class PatientSearchForm(forms.Form):
    """Form for searching patients"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or code (LOL-XXXXX)'
        })
    )


class VisitStep1Form(forms.Form):
    """Step 1: Select or create patient for visit"""
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'patient-select'
        })
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search patient by name or code...'
        })
    )


class VisitStep2Form(forms.ModelForm):
    """Step 2: Reception details for visit"""
    
    class Meta:
        model = Visit
        fields = []  # Snapshot fields are auto-populated from patient
        
    # Additional fields that reception might need to update
    brought_by_update = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Update brought by (if different)'
        })
    )


class VisitClinicianForm(forms.ModelForm):
    """Form for clinician to update visit with diagnosis and treatment"""
    
    class Meta:
        model = Visit
        fields = ['diagnosis', 'treatment_notes', 'next_visit']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter diagnosis'
            }),
            'treatment_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter treatment notes'
            }),
            'next_visit': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class VisitProductForm(forms.ModelForm):
    """Form for adding products/services to a visit"""
    
    class Meta:
        model = VisitProduct
        fields = ['product', 'quantity', 'status']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select product-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = LOLProductService.objects.filter(active=True)


class VisitProductUpdateForm(forms.ModelForm):
    """Form for updating visit product status"""
    
    class Meta:
        model = VisitProduct
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class WorkshopOrderForm(forms.ModelForm):
    """Form for creating/updating workshop orders"""
    
    class Meta:
        model = WorkshopOrder
        fields = ['status', 'expected_ready_date', 'completed_date', 'assigned_to', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_ready_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'completed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about this order'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].required = False


class WorkshopOrderCreateForm(forms.ModelForm):
    """Form for creating workshop orders with visit product selection"""
    visit_product = forms.ModelChoiceField(
        queryset=VisitProduct.objects.filter(status='To Make'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    class Meta:
        model = WorkshopOrder
        fields = ['visit_product', 'status', 'expected_ready_date', 'assigned_to', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_ready_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about this order'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].required = False
        # Filter visit products that don't have workshop orders yet
        self.fields['visit_product'].queryset = VisitProduct.objects.filter(
            status='To Make'
        ).exclude(
            workshop_order__isnull=False
        )


class LOLPaymentForm(forms.ModelForm):
    """Form for creating/updating payments"""
    
    class Meta:
        model = LOLPayment
        fields = [
            'visit', 'visit_product', 'method', 'expected_pay', 
            'amount_paid', 'mpesa_transaction_id', 'payment_date', 'paid_by'
        ]
        widgets = {
            'visit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visit_product': forms.Select(attrs={
                'class': 'form-select'
            }),
            'method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'mpesa_transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'M-Pesa transaction ID (if applicable)'
            }),
            'payment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'paid_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of person making payment'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['visit_product'].required = False
        self.fields['amount_paid'].required = False


class LOLPaymentCreateForm(forms.ModelForm):
    """Simplified form for creating payments from visit context"""
    
    class Meta:
        model = LOLPayment
        fields = [
            'method', 'expected_pay', 'amount_paid', 
            'mpesa_transaction_id', 'paid_by'
        ]
        widgets = {
            'method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'mpesa_transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'M-Pesa transaction ID (if applicable)'
            }),
            'paid_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of person making payment'
            }),
        }


class ExportFilterForm(forms.Form):
    """Form for filtering exports"""
    RANGE_CHOICES = (
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('year', 'This Year'),
        ('custom', 'Custom Range'),
    )
    
    date_range = forms.ChoiceField(
        choices=RANGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
