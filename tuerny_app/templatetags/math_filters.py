from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return round((value / arg) * 100, 1) if arg != 0 else 0
    except (ZeroDivisionError, TypeError, ValueError):
        return 0
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)