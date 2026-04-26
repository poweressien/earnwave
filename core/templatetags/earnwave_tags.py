from django import template
register = template.Library()

@register.filter
def split(value, delimiter):
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    """Get dict item by key — used in daily_challenge template."""
    return dictionary.get(key)

@register.filter
def progress_pct(uc, challenge):
    """Calculate challenge progress percentage."""
    if not uc or challenge.target == 0:
        return 0
    return min(100, int((uc.current_count / challenge.target) * 100))
