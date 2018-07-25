from authentications.apps import InvalidAccessToken
from authentications.models import Authentications
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient
from authentications.utils import get_auth_header as get_header

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.conf import settings

import time
import requests
import logging


def login_user(request):
    next_request = None
    logger = logging.getLogger(__name__)
    if request.POST:
        logger = setup_logger(request, logger, "")
        username = request.POST['username']
        password = request.POST['password']
        logger.info("[{}] ========== Start login from web page ==========".format(username))
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            if 'correlation_id' in request.session:
                correlation_id = request.session['correlation_id']
            logger_new = logging.getLogger(__name__)
            logger_new = setup_logger(request, logger_new, correlation_id)
            login(request, user)
            permissions = get_permission_from_backend(user, logger_new)

            if permissions is not None:
                authens = Authentications.objects.get(user=user)
                authens.permissions = permissions['permissions']
                authens.save()

                request.session['permissions'] = permissions['permissions']

            next_request = request.POST.get('next') or 'web:web-index'
            return redirect(next_request)

    elif request.GET:
        next_request = request.GET['next']

    return render(request, "authentications/login.html", {'next': next_request})


def get_permission_from_backend(username, logger):
    headers = get_header(username)
    url = api_settings.GET_PERMISSION_PATH
    is_success, status_code, data = RestFulClient.get(url=url, headers=headers, loggers=logger)
    if is_success:
        if data is None or data == "":
            return None
        logger.info("[{}] Permissions is [{}]".format(username, len(data)))
        return data


def logout_user(request):
    logger = logging.getLogger(__name__)
    logger = setup_logger(request, logger, request.user)
    username = request.user.username
    logger.info("[{}]========== Start to logout ==========".format(username))
    url = settings.DOMAIN_NAMES + api_settings.LOGOUT_URL
    logger.info("[{}] sends logout request URL: {}".format(username, url))

    try:
        headers = get_auth_header(request.user)
    except Exception as e:
        logger.error(e)
        logout(request)
        logger.info("[{}] ========== Finished to logout ==========".format(username))
        return redirect('authentications:login')

    start_time = time.time()
    response = requests.post(url, headers=headers, verify=settings.CERT)
    end_time = time.time()

    logger.info("[{}] Got logout response Code: {}".format(username, response.status_code))
    logger.info("[{}] Got logout response: {}".format(username, response.text))
    logger.info("[{}] Got logout response time: {} sec.".format(username, end_time - start_time))

    if request.user.is_authenticated:
        auth = Authentications.objects.get(user=request.user)
        if auth is not None:
            logger.info('[{}] Deleting current session info'.format(username))
            auth.delete()
    logout(request)
    logger.info("[{}] Was logged out".format(username, request.user))
    logger.info("[{}] ========== Finished to logout ==========".format(username))

    if request.GET:
        next_request = request.GET['next']
        return render(request, "authentications/login.html", {'next': next_request})

    return redirect('authentications:login')


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
