from .apps import InvalidAccessToken
from web_admin import api_settings

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from .models import Authentications

import time
import requests
import logging

logger = logging.getLogger(__name__)


def logout_user(request):
    logger.info('========== Start to logout ==========')
    url = settings.DOMAIN_NAMES + api_settings.LOGOUT_URL
    username = request.user.username
    logger.info("username {} sends logout request URL: {}".format(username, url))

    try:
        headers = get_auth_header(request.user)
    except Exception as e:
        logger.error(e)
        logout(request)
        logger.info('========== Finished to logout ==========')
        return redirect('login')

    start_time = time.time()
    response = requests.post(url, headers=headers, verify=settings.CERT)
    end_time = time.time()

    logger.info("username {} got logout response Code: {}".format(username, response.status_code))
    logger.info("username {} got logout response: {}".format(username, response.text))
    logger.info("username {} got logout response time: {} sec.".format(username, end_time - start_time))

    if request.user.is_authenticated:
        auth = Authentications.objects.get(user=request.user)
        if auth is not None:
            logger.info('username {} deleting current session info'.format(username))
            auth.delete()
    logout(request)
    logger.info("username {} was logged out".format(username, request.user))
    logger.info('========== Finished to logout ==========')
    return redirect('/admin-portal/')


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
        'content-type': 'application/x-www-form-urlencoded',
        'correlation-id': correlation_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    return headers
