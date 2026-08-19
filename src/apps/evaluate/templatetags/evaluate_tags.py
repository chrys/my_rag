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


@register.filter(name="is_gemini")
def is_gemini(model_name: str) -> bool:
    """
    Returns True if the model name is a Gemini model.
    """
    name = (str(model_name) or "").lower()
    return name.startswith("gemini") or "gemini" in name
