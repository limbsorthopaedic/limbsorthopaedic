
from django.db import models
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field

class Career(models.Model):
    TITLE_CHOICES = [
        ('Orthopaedic Specialist', 'Orthopaedic Specialist'),
        ('Prosthetist', 'Prosthetist'),
        ('Orthotist', 'Orthotist'),
        ('Physiotherapist (Orthopaedic Focused)', 'Physiotherapist (Orthopaedic Focused)'),
        ('Receptionist (Orthopaedic Medical)', 'Receptionist (Orthopaedic Medical)'),
        ('Marketing Specialist (Healthcare)', 'Marketing Specialist (Healthcare)'),
        ('Internship Opportunity (3 Months)', 'Internship Opportunity (3 Months)'),
        ('Other', 'Other'),
    ]
    
    LOCATION_CHOICES = [
        ('Nairobi, Kenya', 'Nairobi, Kenya'),
        ('Other', 'Other'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Internship (3 Months)', 'Internship (3 Months)'),
        ('Cashual', 'Cashual'),
    ]
    
    INDUSTRY_CHOICES = [
        ('Healthcare / Orthopaedics', 'Healthcare / Orthopaedics'),
        ('Other', 'Other'),
    ]
    
    title = models.CharField(max_length=200, choices=TITLE_CHOICES)
    other_title = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    other_location = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    other_industry = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(max_length=500)
    about = CKEditor5Field('About', config_name='extends')
    responsibilities = CKEditor5Field('Responsibilities', config_name='extends')
    requirements = CKEditor5Field('Requirements', config_name='extends')
    benefits = CKEditor5Field('Benefits', config_name='extends')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Careers"

class CareerApplication(models.Model):
    INTERNSHIP_CHOICES = [
        ('Orthopaedic Specialist', 'Orthopaedic Specialist'),
        ('Prosthetist', 'Prosthetist'),
        ('Orthotist', 'Orthotist'),
        ('Physiotherapist', 'Physiotherapist'),
        ('Receptionist', 'Receptionist'),
        ('Marketing Specialist', 'Marketing Specialist'),
        ('Other', 'Other'),
    ]
    
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+\d{1,}$', message='Phone must start with + and country code')]
    )
    job_title = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.career.title}"
        
    def send_job_offer_email(self):
        subject = 'Job Offer from LIMBS Orthopaedic'
        html_message = render_to_string('careers/email/job_offer.html', {'application': self})
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message,
            fail_silently=False,
        )

    def send_rejection_email(self):
        subject = 'Application Status Update - LIMBS Orthopaedic'
        html_message = render_to_string('careers/email/rejection.html', {'application': self})
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message,
            fail_silently=False,
        )
