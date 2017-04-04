from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.models import Authentications

import random
import string
import logging

logger = logging.getLogger(__name__)

def get_auth_header(user):
    client_id = settings.CLIENTID
    client_secret = settings.CLIENTSECRET
    correlation_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    try:
        auth = Authentications.objects.get(user=user)
        access_token = auth.access_token
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
