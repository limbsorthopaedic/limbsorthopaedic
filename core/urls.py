
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.generic import TemplateView
from . import views
from . import search_views
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /adminlimbsorth/",
        "Disallow: /accounts/",
        "Disallow: /staff_chat/",
        "",
        "Sitemap: https://limbsorthopaedic.org/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faqs/', views.FAQView.as_view(), name='faqs'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    
    # Search URLs
    path('search/', search_views.search_results, name='search_results'),
    path('api/search/suggestions/', search_views.search_suggestions, name='search_suggestions'),
    path('api/search/redirect/', search_views.search_redirect, name='search_redirect'),
    
    # Theme API
    path('api/set-theme/', views.set_theme_preference, name='set_theme'),
    path('api/get-theme/', views.get_theme_preference, name='get_theme'),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
]
