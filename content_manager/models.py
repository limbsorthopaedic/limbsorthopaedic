from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify


class PageSection(models.Model):
    """
    A model to store content sections that can be easily managed through the admin interface
    and displayed on different pages using template tags.
    """
    SECTION_TYPES = (
        ('hero', 'Hero Section'),
        ('content', 'Content Section'),
        ('feature', 'Feature Section'),
        ('cta', 'Call to Action'),
        ('gallery', 'Gallery'),
        ('testimonial', 'Testimonial'),
        ('faq', 'FAQ'),
        ('other', 'Other'),
    )
    
    identifier = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique identifier used in templates (e.g., 'home-hero', 'about-intro')"
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    content = CKEditor5Field('Content', config_name='extends', blank=True, null=True)
    image = models.ImageField(upload_to='page_sections/', blank=True, null=True)
    image_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="External image URL (used if no image is uploaded)"
    )
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_url = models.CharField(max_length=255, blank=True, null=True)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='content')
    custom_css_class = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Additional CSS classes to apply to this section"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'identifier']
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
    
    def __str__(self):
        return f"{self.identifier} ({self.get_section_type_display()})"
        
    def get_image(self):
        """Return the image URL (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None


class SiteSetting(models.Model):
    """
    Model to store site-wide settings that can be accessed from any template
    through the context processor.
    """
    key = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique key used to access this setting (e.g., 'contact_email', 'facebook_url')"
    )
    value = models.TextField(default="", help_text="Value of the setting")
    description = models.TextField(blank=True, null=True, help_text="Optional description for this setting")
    is_public = models.BooleanField(
        default=True,
        help_text="If unchecked, this setting will not be available in templates"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['key']
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.key