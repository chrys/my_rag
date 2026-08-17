from django import template

register = template.Library()


@register.filter(name="dict_key")
def dict_key(dictionary, key):
    """
    Returns the value for the given key in a dictionary.
    Usage: {{ my_dict|dict_key:key_name }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""
