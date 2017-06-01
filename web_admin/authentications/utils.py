from authentications.apps import InvalidAccessToken
from authentications.models import Authentications
from authentications.apps import CustomBackend
from django.conf import settings
from django.http import HttpRequest
import logging

logger = logging.getLogger(__name__)


def get_auth_header(user, request):
    client_id = settings.CLIENTID
    client_secret = settings.CLIENTSECRET
    client_ip = CustomBackend().get_client_ip(request)
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
        'client_ip': client_ip,
        'client_secret': client_secret,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    return headers
