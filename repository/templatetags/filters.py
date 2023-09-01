from django import template
import os

register = template.Library()

@register.filter()
def get_item(dictionary, key):
    return getattr(dictionary, key)

@register.filter()
def basename(path):
    return os.path.basename(path)

@register.filter()
def not_in(lista, args):
    notIn = args.split(',')
    if isinstance(lista, dict):
        return [ v for v in list if v not in notIn ]
    if isinstance(lista, list):
        return [ v for v in lista if str(v) not in notIn ]
    return str(lista)
    
@register.filter()
def list_to_string(list, sep):
    return str(sep).join([str(i) for i in list])

@register.filter()
def list_to_string_by_attr(list, args):
    params = args.split(',')
    attr = params[0]
    sep = params[1]
    return str(sep).join([str(getattr(i, attr)) for i in list])