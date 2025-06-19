
from django import forms
from .models import CareerApplication

class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = CareerApplication
        fields = ['career', 'full_name', 'email', 'phone', 'job_title', 'resume']
        
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed")
            if resume.size > 10*1024*1024:  # 10MB limit
                raise forms.ValidationError("File size must be under 10MB")
        return resume
