from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class ServiceCategory(models.Model):
    """Model for service categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    """Model for orthopaedic services"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = CKEditor5Field('Description', config_name='extends')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    # Keeping the original image fields for backward compatibility
    image = models.ImageField(upload_to='services/', blank=True, null=True, 
                              help_text="Legacy field - use ServiceImage for multiple images")
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Legacy field - use ServiceImage for multiple images")
    icon_class = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
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
        return reverse('service_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def whatsapp_message(self):
        """Generate a pre-filled WhatsApp message for this service"""
        service_url = f"https://limbsorthopaedic.org{self.get_absolute_url()}"
        return f"Hello *LIMBS Orthopaedic*, I want {self.title} {service_url}"
        
    def get_image(self):
        """Return the primary image (either from ServiceImage or legacy fields)"""
        # First try to get the first image from ServiceImage
        service_images = self.service_images.all()
        if service_images.exists():
            first_image = service_images.first()
            if first_image.image and hasattr(first_image.image, 'url'):
                return first_image.image.url
            elif first_image.image_url:
                return first_image.image_url
        
        # Fall back to legacy fields
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
            
        return None
        
    def get_all_images(self):
        """Return all images for this service"""
        images = []
        
        # Add images from ServiceImage
        for service_image in self.service_images.all():
            if service_image.image and hasattr(service_image.image, 'url'):
                images.append({
                    'url': service_image.image.url,
                    'alt': service_image.title or self.title,
                    'description': service_image.description
                })
            elif service_image.image_url:
                images.append({
                    'url': service_image.image_url,
                    'alt': service_image.title or self.title,
                    'description': service_image.description
                })
        
        # If no ServiceImage records, add legacy image
        if not images and self.get_image():
            images.append({
                'url': self.get_image(),
                'alt': self.title,
                'description': ''
            })
            
        return images
        
    @property
    def has_multiple_images(self):
        """Check if the service has multiple images"""
        return self.service_images.count() > 1 or (self.service_images.count() == 1 and self.image)


class ServiceImage(models.Model):
    """Model for service images (multiple per service)"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_images')
    title = models.CharField(max_length=200, blank=True, null=True, help_text="Optional title for the image")
    description = models.TextField(blank=True, null=True, help_text="Optional description for the image")
    image = models.ImageField(upload_to='services/images/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Optional external URL for image (used if no image is uploaded)")
    order = models.IntegerField(default=0, help_text="Order of display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        
    def __str__(self):
        return f"{self.service.title} - Image {self.order}"
        
    def get_image(self):
        """Return the image (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
