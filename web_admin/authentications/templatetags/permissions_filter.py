from authentications.models import Authentications
from django import template

register = template.Library()


@register.filter(name='has_permission_name')
def has_permission_name(user, group_name):
    """
    Verify User have permission to see menu
    """
    authens = Authentications.objects.get(user=user)
    permissions = authens.permissions
    return True if group_name in [x['name'] for x in permissions] else False

