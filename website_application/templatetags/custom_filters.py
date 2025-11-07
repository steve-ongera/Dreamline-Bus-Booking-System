# routes/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def filter_by_id(locations, selected_id):
    """
    Finds and returns the name of a location given its ID.
    Usage: {{ locations|filter_by_id:selected_origin }}
    """
    try:
        selected_id = int(selected_id)
    except (ValueError, TypeError):
        return ""

    for location in locations:
        # Handle both queryset and dict-like structures
        if hasattr(location, 'id') and location.id == selected_id:
            return getattr(location, 'name', str(location))
        elif isinstance(location, dict) and location.get('id') == selected_id:
            return location.get('name', '')

    return ""
