import logging
from django.conf import settings
from web_admin import api_settings
from . import put_client

logger = logging.getLogger(__name__)


def suspend(request, client_id):
    url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CLIENT_URL.format(client_id)
    return put_client.put_client(request=request, url=url, title='suspend',
                                 logger=logger, client_id=client_id)
