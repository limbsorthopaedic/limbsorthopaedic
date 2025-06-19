from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field


class BlogCategory(models.Model):
    """Model for blog categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Model for blog posts"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='blog_posts')
    content = CKEditor5Field('Content', config_name='extends')
    summary = CKEditor5Field('Summary', config_name='default', help_text="A brief summary of the post for previews")
    categories = models.ManyToManyField(BlogCategory, related_name='posts')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    featured_image_url = models.URLField(max_length=500, blank=True, null=True, 
                                        help_text="Optional external URL for featured image (used if no image is uploaded)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_date', '-created_date']
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_featured_image(self):
        """Return the featured image (either uploaded file or external URL)"""
        if self.featured_image and hasattr(self.featured_image, 'url'):
            return self.featured_image.url
        elif self.featured_image_url:
            return self.featured_image_url
        return None
        
    def get_image(self):
        """Return the featured image (either uploaded file or external URL)"""
        return self.get_featured_image()


class Comment(models.Model):
    """Model for blog comments"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
    
    class Meta:
        ordering = ['-created_date']
