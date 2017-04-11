from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from .models import Authentications
from .apps import InvalidAccessToken
import time
import random
import string
import requests
import logging

logger = logging.getLogger(__name__)

def logout_user(request):
    url = settings.LOGOUT_URL
    username = request.user.username
    logger.info("username {} sends logout request URL: {}".format(username, url))

    try:
        auth = Authentications.objects.get(user=request.user)
        access_token = auth.access_token
        logger.info("logout access_token: {}".format(access_token))
    except Exception as e:
        raise InvalidAccessToken("{}".format(e))

    headers = get_auth_header(request.user)

    start_time = time.time()
    response = requests.post(url, headers=headers, verify=settings.CERT)
    end_time = time.time()
    logger.info("username {} got logout response Code: {}".format(username, response.status_code))
    logger.info("username {} got logout response: {}".format(username, response.content))
    logger.info("username {} got logout response time: {} sec.".format(username, end_time - start_time))

    response_json = response.json()

    if response.status_code == 200:
        status = response_json['status']
        if status['code'] == "success":
            if request.user.is_authenticated:
                auth = Authentications.objects.get(user=request.user)
                if auth is not None:
                    logger.info('username {} deleting current session info'.format(username))
                    auth.delete()
            logout(request)
            logger.info("username {} was logged out".format(username, request.user))
            return redirect('/admin-portal/')
        else:
            pass
    else:
        code = response_json.get('status', {}).get('code', '')
        if (code is not None) and (code == 'access_token_expire'):
            raise InvalidAccessToken()

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
        'content-type': 'application/x-www-form-urlencoded',
        'correlation-id': correlation_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    return headers