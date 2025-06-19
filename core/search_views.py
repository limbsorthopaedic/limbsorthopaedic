"""
Search functionality for LIMBS Orthopaedic website
Provides comprehensive search across services, products, and other content
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from services.models import Service, ServiceCategory
from products.models import Product, ProductCategory
from blog.models import BlogPost, BlogCategory
from core.models import TeamMember, HeroSlide
from testimonials.models import Testimonial
from appointments.models import Appointment
from content_manager.models import PageSection, SiteSetting
from accounts.models import Doctor


@require_http_methods(["GET"])
def search_suggestions(request):
    """
    API endpoint for search suggestions as user types
    Returns JSON with suggestions for services, products, and other content
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Search services - enhanced search with prioritized results
    services = Service.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).select_related('category').order_by('-featured', 'order', 'title')[:6]
    
    for service in services:
        # Prioritize title matches
        match_in_title = query.lower() in service.title.lower()
        suggestions.append({
            'type': 'service',
            'title': service.title,
            'description': service.description[:120] + '...' if len(service.description) > 120 else service.description,
            'url': service.get_absolute_url(),
            'icon': service.icon_class or 'fas fa-hand-holding-medical',
            'category': 'Services',
            'priority': 1 if match_in_title else 2
        })
    
    # Search products - enhanced search with prioritized results
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).select_related('category').order_by('-featured', 'order', 'title')[:6]
    
    for product in products:
        # Prioritize title matches
        match_in_title = query.lower() in product.title.lower()
        price_text = f"${product.price}" if product.price else "Price on request"
        suggestions.append({
            'type': 'product',
            'title': product.title,
            'description': f"{product.description[:100]}... • {price_text}" if len(product.description) > 100 else f"{product.description} • {price_text}",
            'url': product.get_absolute_url(),
            'icon': 'fas fa-box-open',
            'category': 'Products',
            'priority': 1 if match_in_title else 2
        })
    
    # Search blog posts - enhanced to include more fields
    blog_posts = BlogPost.objects.filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) | 
        Q(summary__icontains=query) |
        Q(meta_description__icontains=query) if hasattr(BlogPost.objects.model, 'meta_description') else Q() |
        Q(tags__name__icontains=query) if hasattr(BlogPost.objects.model, 'tags') else Q(),
        status='published'
    )[:3]
    
    for post in blog_posts:
        suggestions.append({
            'type': 'blog',
            'title': post.title,
            'description': post.summary[:100] + '...' if post.summary and len(post.summary) > 100 else post.summary,
            'url': f'/blog/{post.slug}/' if hasattr(post, 'slug') else f'/blog/{post.id}/',
            'icon': 'fas fa-newspaper',
            'category': 'Blog'
        })
    
    # Search team members
    team_members = TeamMember.objects.filter(
        Q(name__icontains=query) | Q(title__icontains=query) | Q(bio__icontains=query)
    )[:2]
    
    for member in team_members:
        suggestions.append({
            'type': 'team',
            'title': member.name,
            'description': f"{member.title} - {member.bio[:80]}..." if member.bio else member.title,
            'url': '/about/#team',
            'icon': 'fas fa-user-md',
            'category': 'Team'
        })
    
    # Search testimonials
    testimonials = Testimonial.objects.filter(
        Q(name__icontains=query) | Q(content__icontains=query) | Q(title__icontains=query),
        is_approved=True
    )[:2]
    
    for testimonial in testimonials:
        suggestions.append({
            'type': 'testimonial',
            'title': f"Testimonial from {testimonial.name}",
            'description': testimonial.content[:100] + '...' if len(testimonial.content) > 100 else testimonial.content,
            'url': '/testimonials/',
            'icon': 'fas fa-comment-alt',
            'category': 'Testimonials'
        })
    
    # Search doctors
    doctors = Doctor.objects.filter(
        Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(specialty__icontains=query),
        is_active=True
    )[:2]
    
    for doctor in doctors:
        suggestions.append({
            'type': 'doctor',
            'title': f"Dr. {doctor.user.get_full_name()}",
            'description': f"Specialist in {doctor.specialty}",
            'url': '/about/#team',
            'icon': 'fas fa-user-md',
            'category': 'Doctors'
        })
    
    # Search service categories
    service_categories = ServiceCategory.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    )[:2]
    
    for category in service_categories:
        suggestions.append({
            'type': 'service_category',
            'title': category.name,
            'description': category.description[:100] + '...' if category.description and len(category.description) > 100 else category.description,
            'url': '/services/',
            'icon': 'fas fa-list',
            'category': 'Service Categories'
        })
    
    # Search product categories
    product_categories = ProductCategory.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    )[:2]
    
    for category in product_categories:
        suggestions.append({
            'type': 'product_category',
            'title': category.name,
            'description': category.description[:100] + '...' if category.description and len(category.description) > 100 else category.description,
            'url': '/products/',
            'icon': 'fas fa-tags',
            'category': 'Product Categories'
        })
    
    # Search page sections (content manager)
    page_sections = PageSection.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query) | Q(subtitle__icontains=query),
        is_active=True
    )[:3]
    
    for section in page_sections:
        page_url = '/'
        if section.page == 'about':
            page_url = '/about/'
        elif section.page == 'contact':
            page_url = '/contact/'
        elif section.page == 'services':
            page_url = '/services/'
        elif section.page == 'products':
            page_url = '/products/'
        
        suggestions.append({
            'type': 'page_section',
            'title': section.title,
            'description': section.subtitle or (section.content[:100] + '...' if len(section.content) > 100 else section.content),
            'url': page_url,
            'icon': 'fas fa-puzzle-piece',
            'category': 'Page Content'
        })
    
    # Search hero slides
    hero_slides = HeroSlide.objects.filter(
        Q(title__icontains=query) | Q(subtitle__icontains=query) | Q(content__icontains=query),
        is_active=True
    )[:2]
    
    for slide in hero_slides:
        suggestions.append({
            'type': 'hero_slide',
            'title': slide.title,
            'description': slide.subtitle or slide.content[:100] + '...' if len(slide.content) > 100 else slide.content,
            'url': '/',
            'icon': 'fas fa-home',
            'category': 'Home Page'
        })
    
    # Add static page suggestions based on query
    static_suggestions = []
    if any(word in query.lower() for word in ['about', 'company', 'history', 'team', 'mission', 'vision']):
        static_suggestions.append({
            'type': 'page',
            'title': 'About Us',
            'description': 'Learn about LIMBS Orthopaedic and our mission',
            'url': '/about/',
            'icon': 'fas fa-info-circle',
            'category': 'Pages'
        })
    
    if any(word in query.lower() for word in ['contact', 'phone', 'address', 'location', 'reach', 'call', 'email']):
        static_suggestions.append({
            'type': 'page',
            'title': 'Contact Us',
            'description': 'Get in touch with LIMBS Orthopaedic',
            'url': '/contact/',
            'icon': 'fas fa-phone',
            'category': 'Pages'
        })
    
    if any(word in query.lower() for word in ['appointment', 'book', 'schedule', 'visit', 'consultation']):
        static_suggestions.append({
            'type': 'page',
            'title': 'Book Appointment',
            'description': 'Schedule your appointment with us',
            'url': '/appointments/',
            'icon': 'fas fa-calendar-check',
            'category': 'Pages'
        })
    
    if any(word in query.lower() for word in ['gallery', 'photos', 'images', 'pictures', 'facility']):
        static_suggestions.append({
            'type': 'page',
            'title': 'Gallery',
            'description': 'View our facility and work',
            'url': '/gallery/',
            'icon': 'fas fa-images',
            'category': 'Pages'
        })
    
    if any(word in query.lower() for word in ['testimonial', 'review', 'feedback', 'patient', 'experience']):
        static_suggestions.append({
            'type': 'page',
            'title': 'Testimonials',
            'description': 'Read what our patients say about us',
            'url': '/testimonials/',
            'icon': 'fas fa-comment-alt',
            'category': 'Pages'
        })
    
    if any(word in query.lower() for word in ['blog', 'news', 'article', 'post', 'updates']):
        static_suggestions.append({
            'type': 'page',
            'title': 'Blog',
            'description': 'Read our latest articles and updates',
            'url': '/blog/',
            'icon': 'fas fa-newspaper',
            'category': 'Pages'
        })
    
    suggestions.extend(static_suggestions[:2])
    
    # Sort suggestions by priority (services and products with title matches first)
    suggestions.sort(key=lambda x: (x.get('priority', 3), x.get('category', 'ZZZ')))
    
    return JsonResponse({'suggestions': suggestions[:12]})


@require_http_methods(["GET"])
def search_results(request):
    """
    Main search results page
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    # Search services - comprehensive search
    services = Service.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(name__icontains=query) |
        Q(content__icontains=query) if hasattr(Service.objects.model, 'content') else Q(),
        is_active=True
    )
    
    # Search products - comprehensive search
    products = Product.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(name__icontains=query) |
        Q(features__icontains=query) if hasattr(Product.objects.model, 'features') else Q() |
        Q(specifications__icontains=query) if hasattr(Product.objects.model, 'specifications') else Q(),
        is_active=True
    )
    
    # Search blog posts - comprehensive search
    blog_posts = BlogPost.objects.filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) | 
        Q(summary__icontains=query) |
        Q(meta_description__icontains=query) if hasattr(BlogPost.objects.model, 'meta_description') else Q() |
        Q(tags__name__icontains=query) if hasattr(BlogPost.objects.model, 'tags') else Q(),
        status='published'
    )
    
    # Search team members
    team_members = TeamMember.objects.filter(
        Q(name__icontains=query) | Q(title__icontains=query) | Q(bio__icontains=query)
    )
    
    # Search testimonials
    testimonials = Testimonial.objects.filter(
        Q(name__icontains=query) | Q(content__icontains=query) | Q(title__icontains=query),
        is_approved=True
    )
    
    # Search doctors
    doctors = Doctor.objects.filter(
        Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(specialty__icontains=query),
        is_active=True
    )
    
    # Search service categories
    service_categories = ServiceCategory.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    )
    
    # Search product categories
    product_categories = ProductCategory.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    )
    
    # Search page sections (content manager)
    page_sections = PageSection.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query) | Q(subtitle__icontains=query),
        is_active=True
    )
    
    # Search hero slides
    hero_slides = HeroSlide.objects.filter(
        Q(title__icontains=query) | Q(subtitle__icontains=query) | Q(content__icontains=query),
        is_active=True
    )
    
    # Calculate total results
    total_results = (services.count() + products.count() + blog_posts.count() + 
                    team_members.count() + testimonials.count() + doctors.count() + 
                    service_categories.count() + product_categories.count() + 
                    page_sections.count() + hero_slides.count())
    
    context = {
        'query': query,
        'services': services,
        'products': products,
        'blog_posts': blog_posts,
        'team_members': team_members,
        'testimonials': testimonials,
        'doctors': doctors,
        'service_categories': service_categories,
        'product_categories': product_categories,
        'page_sections': page_sections,
        'hero_slides': hero_slides,
        'total_results': total_results,
    }
    
    return render(request, 'core/search_results.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def search_redirect(request):
    """
    Handle search form submission and redirect to appropriate page
    """
    try:
        data = json.loads(request.body)
        search_type = data.get('type')
        url = data.get('url')
        
        if search_type and url:
            return JsonResponse({'redirect_url': url})
        else:
            # Fallback to search results page
            query = data.get('query', '')
            return JsonResponse({'redirect_url': f'/search/?q={query}'})
            
    except json.JSONDecodeError:
        # Handle regular form submission
        query = request.POST.get('q', '').strip()
        if query:
            return redirect('search_results')
        return redirect('home')