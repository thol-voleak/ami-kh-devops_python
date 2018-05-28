import json

from django import template
from django.utils.safestring import mark_safe

from web_admin.utils import encode_current_url_for_back, get_back_url, has_any_permission

register = template.Library()


@register.filter(name='split')
def filter_split(str, c):
    return str.split(c)


@register.filter(name='jsonify')
def filter_json(value):
    return mark_safe(json.dumps(value))


@register.filter(name='has_any_permission')
def filter_has_any_permission(request, args):
    return has_any_permission(request, args.split(','))


@register.simple_tag(name='current_url_encoded_for_back', takes_context=True)
def tag_current_url_encoded_for_back(context):
    request = context['request']
    return encode_current_url_for_back(request)


@register.simple_tag(name='get_back_url', takes_context=True)
def tag_get_back_url(context, default_url=None):
    request = context['request']
    return get_back_url(request, default_url)