from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Testimonial
from core.models import SocialMedia


class TestimonialListView(ListView):
    """View for displaying testimonials"""
    model = Testimonial
    template_name = 'testimonials/testimonials.html'
    context_object_name = 'testimonials'
    paginate_by = 10
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_approved=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_testimonials'] = Testimonial.objects.filter(is_approved=True, is_featured=True)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle testimonial submission"""
        name = request.POST.get('name')
        title = request.POST.get('title')
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        
        if name and content and rating:
            Testimonial.objects.create(
                name=name,
                title=title,
                content=content,
                rating=int(rating)
            )
            messages.success(request, 'Thank you for your testimonial! It will be reviewed and published soon.')
        else:
            messages.error(request, 'Please fill in all the required fields.')
        
        return redirect('testimonials')
