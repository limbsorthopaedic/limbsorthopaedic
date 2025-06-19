from django.db import models


class HeroSlide(models.Model):
    """Model for hero carousel slides on the home page"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300)
    content = models.TextField()
    cta_text = models.CharField(max_length=100, verbose_name="Call to Action Text")
    cta_link = models.CharField(max_length=200, default="/appointments/", verbose_name="Call to Action Link")
    image = models.ImageField(upload_to='hero_slides/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Optional external URL for background image (used if no image is uploaded)")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Order in which slides appear (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"
    
    def get_image(self):
        """Return the image (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
        
    def get_cta_link(self):
        """Ensure the CTA link is using the correct URL path"""
        # Always return the appointments URL regardless of what's stored
        # This is a safety measure to ensure the link always works
        if self.cta_link == '/appointment/':
            return '/appointments/'
        return self.cta_link


class TeamMember(models.Model):
    """Model for team members displayed on the About page"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Optional external URL for image (used if no image is uploaded)")
    linkedin_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']
        
    def get_image(self):
        """Return the image (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None


class Contact(models.Model):
    """Model for contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


class SocialMedia(models.Model):
    """Model for social media links"""
    platform = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, help_text="Font Awesome class for icon")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.platform
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Social Media"
