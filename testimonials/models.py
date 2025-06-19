from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    """Model for patient testimonials"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 'Prosthetic User' or 'Parent of Club Foot Patient'")
    content = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars",
        default=5
    )
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                              help_text="Optional external URL for image (used if no image is uploaded)")
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        
    def get_image(self):
        """Return the image (either uploaded file or external URL)"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None
