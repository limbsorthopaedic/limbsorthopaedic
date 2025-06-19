from django.core.cache import cache
from .models import SiteSetting, PageSection


def site_settings(request):
    """
    Context processor that adds site settings to the context of all templates.
    """
    # Use cache to avoid database queries on every request
    settings_dict = cache.get('site_settings')
    
    if not settings_dict:
        # Get all public settings from the database
        settings = SiteSetting.objects.filter(is_public=True)
        settings_dict = {setting.key: setting.value for setting in settings}
        
        # Cache for 5 minutes
        cache.set('site_settings', settings_dict, 300)
    
    return {'site_settings': settings_dict}


def page_sections(request):
    """
    Context processor that adds page sections to the context of all templates.
    """
    # This context processor doesn't load all sections to avoid unnecessary database queries
    # Instead, the template tags will handle loading specific sections as needed
    return {
        'has_page_sections': True  # Flag to indicate that page sections are available
    }