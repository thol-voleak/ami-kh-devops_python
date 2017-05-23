from django.conf import settings
from django.http import HttpResponse

from web_admin.restful_methods import RESTfulMethods

import logging

logger = logging.getLogger(__name__)


def activate(request, client_id):
    url = settings.ACTIVATE_CLIENT_URL.format(client_id)
    params = {
        'status': 'active',
    }

    data, success = RESTfulMethods._put_method(url, "client", logger, params)
    if success:
        return HttpResponse(status=200, content=data)
    return HttpResponse(status=500, content=data)