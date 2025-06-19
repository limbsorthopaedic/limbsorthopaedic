from django import forms
from .models import CustomProductRequest


class CustomProductRequestForm(forms.ModelForm):
    """Form for custom product requests"""
    class Meta:
        model = CustomProductRequest
        fields = ['name', 'email', 'phone', 'details']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400',
                'id': 'custom-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400',
                'id': 'custom-email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400',
                'id': 'custom-phone'
            }),
            'details': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 4,
                'placeholder': 'Please describe what you need...',
                'id': 'custom-details'
            }),
        }