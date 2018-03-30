from django import template

from web_admin.utils import encode_current_url_for_back, get_back_url

register = template.Library()


@register.simple_tag(name='current_url_encoded_for_back', takes_context=True)
def tag_current_url_encoded_for_back(context):
    request = context['request']
    return encode_current_url_for_back(request)


@register.simple_tag(name='get_back_url', takes_context=True)
def tag_get_back_url(context, default_url=None):
    request = context['request']
    return get_back_url(request, default_url)