from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def notification_badge(count):
    """
    Render a notification badge with the given count.
    If count is 0, returns an empty string.
    """
    if count <= 0:
        return ''
    
    # Apply different classes based on count
    if count > 99:
        count_display = '99+'
        bg_class = 'bg-danger'
    else:
        count_display = str(count)
        if count > 9:
            bg_class = 'bg-warning'
        else:
            bg_class = 'bg-primary'
    
    return format_html(
        '<span class="badge {} badge-pill">{}</span>',
        bg_class, count_display
    )

@register.simple_tag(takes_context=True)
def category_notification_count(context, category_id):
    """
    Return the notification count for a specific category
    """
    if 'notification_counts_by_category' not in context:
        return 0
    
    return context['notification_counts_by_category'].get(str(category_id), 0)