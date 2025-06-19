from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json  # ← Needed for JSON serialization

from .seo import SEOManager
from .models import TeamMember, SocialMedia, HeroSlide
from .forms import ContactForm
from services.models import Service
from products.models import Product
from blog.models import BlogPost
from testimonials.models import Testimonial


def set_theme_preference(request):
    theme = request.GET.get('theme', 'light')
    response = JsonResponse({'status': 'success'})
    response.set_cookie('theme_preference', theme, max_age=365*24*60*60)  # 1 year
    return response

def get_theme_preference(request):
    theme = request.COOKIES.get('theme_preference', 'light')
    return JsonResponse({'theme': theme})


class HomeView(TemplateView):
    """View for the home page"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True).order_by('order')
        context['featured_services'] = Service.objects.filter(featured=True)[:4]
        context['featured_products'] = Product.objects.filter(featured=True, is_active=True)[:4]
        context['recent_blogs'] = BlogPost.objects.filter(status='published').order_by('-published_date')[:3]
        context['testimonials'] = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:5]
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        
        # SEO data
        context['meta_keywords'] = SEOManager.get_meta_keywords()
        structured_data = SEOManager.generate_structured_data(self.request)
        context['structured_data'] = [json.dumps(schema, indent=2) for schema in structured_data]
        breadcrumbs = [('Home', '/')]
        breadcrumb_schema = SEOManager.get_breadcrumb_schema(self.request, breadcrumbs)
        context['breadcrumb_schema'] = json.dumps(breadcrumb_schema, indent=2)
        
        return context


class AboutView(TemplateView):
    """View for the about page"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team_members'] = TeamMember.objects.filter(is_active=True)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        
        # SEO data
        context['meta_keywords'] = 'orthopaedic clinic Nairobi, prosthetics Kenya, orthotic specialists, LIMBS team, medical professionals'
        structured_data = SEOManager.generate_structured_data(self.request)
        context['structured_data'] = [json.dumps(schema, indent=2) for schema in structured_data]
        breadcrumbs = [('Home', '/'), ('About Us', '/about/')]
        breadcrumb_schema = SEOManager.get_breadcrumb_schema(self.request, breadcrumbs)
        context['breadcrumb_schema'] = json.dumps(breadcrumb_schema, indent=2)

        return context


class ContactView(CreateView):
    """View for the contact page and form submission"""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your message has been sent. We will get back to you soon!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)

        # SEO (optional – include if needed)
        structured_data = SEOManager.generate_structured_data(self.request)
        context['structured_data'] = [json.dumps(schema, indent=2) for schema in structured_data]
        breadcrumbs = [('Home', '/'), ('Contact', '/contact/')]
        breadcrumb_schema = SEOManager.get_breadcrumb_schema(self.request, breadcrumbs)
        context['breadcrumb_schema'] = json.dumps(breadcrumb_schema, indent=2)

        return context


class FAQView(TemplateView):
    """View for the FAQs page"""
    template_name = 'core/faqs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


class TermsOfServiceView(TemplateView):
    """View for Terms of Service page"""
    template_name = 'core/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


class PrivacyPolicyView(TemplateView):
    """View for Privacy Policy page"""
    template_name = 'core/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


def set_cookie_example(request):
    response = HttpResponse("Cookie set!")
    response.set_cookie('user_preference', 'dark_mode', max_age=365*24*60*60)  # 1 year
    return response

def get_cookie_example(request):
    user_pref = request.COOKIES.get('user_preference', 'light_mode')  # default to light_mode
    return HttpResponse(f"Your preference is: {user_pref}")

def delete_cookie_example(request):
    response = HttpResponse("Cookie deleted!")
    response.delete_cookie('user_preference')
    return response


def set_theme(request):
    """Set theme preference cookie"""
    theme = request.GET.get('theme', 'light')
    response = HttpResponseRedirect('/')
    response.set_cookie('theme_preference', theme, max_age=365*24*60*60)  # 1 year
    return response

def get_theme(request):
    """Get current theme from cookie"""
    theme = request.COOKIES.get('theme_preference', 'light')
    return HttpResponse(f"Current theme: {theme}")
