from django.core.checks import messages

from authentications.apps import InvalidAccessToken
from authentications.models import Authentications
from django import template
from django.conf import settings
from django.core.cache import cache

import logging

from web_admin import setup_logger

register = template.Library()

logger = logging.getLogger(__name__)


@register.filter('has_permission_name')
def has_permission_name(user, group_name):
    """
    Verify User have permission to see menu
    """
    authens = Authentications.objects.get(user=user)
    permissions = authens.permissions
    return True if group_name in [x['name'] for x in permissions] else False


def get_auth_header(user):
    client_id = settings.CLIENTID
    client_secret = settings.CLIENTSECRET
    try:
        auth = Authentications.objects.get(user=user)
        access_token = auth.access_token
        correlation_id = auth.correlation_id
    except Exception as e:
        raise InvalidAccessToken("{}".format(e))
    headers = {
        'content-type': 'application/json',
        'correlation-id': correlation_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    return headers


def get_correlation_id_from_username(user):
    try:
        auth = Authentications.objects.get(user=user)
        return auth.correlation_id
    except Exception as e:
        # logger.error(e)
        return None


def check_permissions_by_user(user, permission):
    if cache.get(user.username):
        if permission in cache.get(user.username):
            return True
        else:
            return False
    else:
        try:
            authens = Authentications.objects.get(user=user)
            permissions = authens.permissions
            return True if permission in [x['name'] for x in permissions] else False
        except Exception as e:
            return False
