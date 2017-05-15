from django.apps import AppConfig
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

import requests
import random
import string
import logging
import time

from authentications.models import Authentications

logger = logging.getLogger(__name__)


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class InvalidAccessToken(Exception):
    """Raised when the access token is invalid"""
    pass


class InvalidAccessTokenException(object):
    def process_exception(self, request, exception):
        if type(exception) == InvalidAccessToken:
            logout(request)
            return HttpResponseRedirect(request.path)
        return None


class CustomBackend:
    def __init__(self):
        pass

    def authenticate(self, username=None, password=None):
        try:
            logger.info('========== Start authentication backend service ==========')
            client_id = settings.CLIENTID
            client_secret = settings.CLIENTSECRET
            url = settings.LOGIN_URL

            logger.info('Auth URL: {}'.format(url))

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            payload = {
                'username': username,
                'password': password,
                'grant_type': 'password',
                'client_id': client_id
            }

            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'correlation-id': "{}-login".format(username),
                'client_id': client_id,
                'client_secret': client_secret,
            }

            logger.info('Calling authentication backend')

            start_date = time.time()
            auth_response = requests.post(url, params=payload, headers=headers, verify=settings.CERT)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))
            logger.info("Authentication response is {}".format(auth_response.text))

            if auth_response.status_code == 200:
                json_data = auth_response.json()
                access_token = json_data.get('access_token')
                correlation_id = json_data.get('correlation_id')

                if (access_token is not None) and (len(access_token) > 0):
                    logger.info('Checking user is exit in system')
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        logger.info('{} user was created', username)
                        user.is_staff = True
                        user.save()

                    logger.info("Adding access token for {} user name".format(username))
                    auth, created_token = Authentications.objects.get_or_create(user=user)
                    auth.access_token = access_token
                    auth.correlation_id = correlation_id
                    auth.save()

                    logger.info("Authentication success and generate session for {} user name".format(username))
                    logger.info('========== Finish authentication backend service ==========')
                    return user
                else:
                    logger.error("Cannot get access token from response of {} user name".format(username))
                    logger.info('========== Finish authentication backend service ==========')
                    return None

        except Exception as ex:
            logger.error(ex)
            logger.error("{} user name authentication to backend was failed".format(username))
            logger.info('========== Finish authentication backend service ==========')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
