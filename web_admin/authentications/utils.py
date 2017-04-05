from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.models import Authentications

import random
import string
import logging
import datetime

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


def format_date_time(data):
    for item in data:
        if (item['created_timestamp'] is not None) and (item['created_timestamp'] != "null"):
            created_at = item['created_timestamp'] / 1000.0
            item['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')

        if (item['last_updated_timestamp'] is not None) and (
                    item['last_updated_timestamp'] != "null"):
            created_at = item['last_updated_timestamp'] / 1000.0
            item['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')
    return data
