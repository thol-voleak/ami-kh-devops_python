import logging
from web_admin import api_settings
from django.http import HttpResponse
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


def suspend(client_id):
    params = {
        'status': 'suspend',
    }

    url = api_settings.SUSPEND_CLIENT_URL.format(client_id)
    data, success = RESTfulMethods._put_method(url, 'client', logger, params)

    if success:
        return HttpResponse(status=200, content=data)
    return HttpResponse(status=500, content=data)
