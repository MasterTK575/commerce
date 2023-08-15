from django import template

register = template.Library()

@register.filter
def get_item(value, arg):
    """Retrieve an item from the list by index."""
    return value[arg]