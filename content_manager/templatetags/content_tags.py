from django import template
from django.utils.safestring import mark_safe
from content_manager.models import PageSection

register = template.Library()


@register.simple_tag
def get_content(identifier, default=""):
    """
    Returns the content of a page section with the given identifier.
    
    Usage:
        {% get_content 'home-hero-title' %}
        {% get_content 'global-footer-text' 'Default text' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        if section.content:
            return mark_safe(section.content)
        return default
    except PageSection.DoesNotExist:
        return default


@register.simple_tag
def get_title(identifier, default=""):
    """
    Returns the title of a page section with the given identifier.
    
    Usage:
        {% get_title 'home-hero-title' %}
        {% get_title 'services-intro-title' 'Our Services' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        if section.title:
            return section.title
        return default
    except PageSection.DoesNotExist:
        return default


@register.simple_tag
def get_subtitle(identifier, default=""):
    """
    Returns the subtitle of a page section with the given identifier.
    
    Usage:
        {% get_subtitle 'home-hero-subtitle' %}
        {% get_subtitle 'services-intro-subtitle' 'Discover our specialized services' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        if section.subtitle:
            return section.subtitle
        return default
    except PageSection.DoesNotExist:
        return default


@register.simple_tag
def get_image(identifier, default=""):
    """
    Returns the image URL of a page section with the given identifier.
    
    Usage:
        {% get_image 'home-hero-image' %}
        {% get_image 'services-intro-image' '/static/images/default.jpg' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        image_url = section.get_image()
        if image_url:
            return image_url
        return default
    except PageSection.DoesNotExist:
        return default


@register.simple_tag
def get_button(identifier, default_text="", default_url="#"):
    """
    Returns HTML for a button from a page section with the given identifier.
    
    Usage:
        {% get_button 'home-cta-button' %}
        {% get_button 'services-cta-button' 'Learn More' '/services/' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        if section.button_text and section.button_url:
            return mark_safe(f'<a href="{section.button_url}" class="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-300">{section.button_text}</a>')
        elif default_text and default_url:
            return mark_safe(f'<a href="{default_url}" class="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-300">{default_text}</a>')
        return ""
    except PageSection.DoesNotExist:
        if default_text and default_url:
            return mark_safe(f'<a href="{default_url}" class="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-300">{default_text}</a>')
        return ""


@register.inclusion_tag('content_manager/section.html')
def render_section(identifier):
    """
    Renders a complete page section with the given identifier.
    
    Usage:
        {% render_section 'home-hero' %}
        {% render_section 'services-intro' %}
    """
    try:
        section = PageSection.objects.get(identifier=identifier, is_active=True)
        return {'section': section}
    except PageSection.DoesNotExist:
        return {'section': None}