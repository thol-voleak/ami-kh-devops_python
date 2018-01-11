from django import template
from django.core import urlresolvers
from django.conf.urls import RegexURLPattern, RegexURLResolver


register = template.Library()


@register.simple_tag(name='check_valid_url', takes_context=True)
def check_valid_url(context, url, apps):
    request = context['request']
    portal_urls = request.session.get('portal_urls')
    if not portal_urls:
        portal_urls = setup_url(request)
    apps = apps.split(',')

    try:
        return check_url(url, apps, portal_urls)
    except KeyError:
        urls_dict = setup_url(request)
        return check_url(url, apps, urls_dict)


def get_urls(urls):
    result = {}
    for obj in urls.url_patterns:
        if isinstance(obj, RegexURLResolver):
            result[obj.app_name] = []
            for url in obj.url_patterns:
                if isinstance(url, RegexURLPattern):
                    result[obj.app_name].append(url.name)
    return result


def setup_url(request):
    urls_obj = urlresolvers.get_resolver()
    urls_dict = get_urls(urls_obj)
    request.session['portal_urls'] = urls_dict
    return urls_dict


def check_url(url, apps, urls_dict):
    for app in apps:
        if url in urls_dict[app]:
            return True
    return False

@register.simple_tag(name='remove_dupplicate_message', takes_context=True)
def remove_dupplicate_message(context, messages):
    custom_message = []
    for msg in messages:
        custom_message.append(msg.message)
    return list(set(custom_message))