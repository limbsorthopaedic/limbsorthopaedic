from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service, ServiceCategory
from core.models import SocialMedia


class ServiceListView(ListView):
    """View to display all services"""
    model = Service
    template_name = 'services/services.html'
    context_object_name = 'services'
    # Removed pagination limit to show all services

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).order_by('order', 'title')
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('category')

        # SEO data
        # Placeholder for SEOManager. Replace with your actual SEO implementation.
        context['meta_keywords'] = 'Aeroplane splint, AFO (Adult), AFO (Child), Arch support, Axillary crutch'
        # context['meta_keywords'] = SEOManager.get_service_keywords() # Original
        # context['structured_data'] = SEOManager.generate_structured_data(self.request) # Original
        context['structured_data'] = {} # Modified
        context['breadcrumbs'] = [('Home', '/'), ('Services', '/services/')]
        # context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(self.request, context['breadcrumbs']) # Original
        context['breadcrumb_schema'] = {} # Modified

        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


class ServiceDetailView(DetailView):
    """View to display a single service"""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        # SEO data
        context['meta_keywords'] = f"{service.title}, {service.category.name}, orthopaedic services Kenya, rehabilitation Nairobi"
        # context['structured_data'] = SEOManager.generate_structured_data(
        #     self.request,
        #     page_type='service',
        #     name=service.title,
        #     description=service.description
        # )
        context['structured_data'] = {} # Modified
        context['breadcrumbs'] = [
            ('Home', '/'),
            ('Services', '/services/'),
            (service.title, f'/services/{service.slug}/')
        ]
        # context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(self.request, context['breadcrumbs'])
        context['breadcrumb_schema'] = {} # Modified

        context['related_services'] = Service.objects.filter(
            category=service.category,
            is_active=True
        ).exclude(id=service.id)[:4]
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context