from authentications.models import Authentications
from web_admin import api_settings

from django.apps import AppConfig
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib import messages
from web_admin.utils import setup_logger
import requests
import logging
import time

from web_admin.utils import encrypt_text

logger = logging.getLogger(__name__)


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class InvalidAccessToken(Exception):
    """Raised when the access token is invalid"""
    pass


class InvalidAccessTokenException(object):
    def process_exception(self, request, exception):
        if type(exception) == InvalidAccessToken:
            messages.add_message(request, messages.INFO,
                                 'Your login credentials have expired. Please login again.')
            logout(request)
            return HttpResponseRedirect(request.path)
        return None


class CustomBackend:
    def __init__(self):
        pass

    def authenticate(self, request=None, username=None, password=None):
        try:
            self.logger = setup_logger(request, logger)
            self.logger.info('========== Start authentication backend service ==========')
            client_id = settings.CLIENTID
            client_secret = settings.CLIENTSECRET
            url = settings.DOMAIN_NAMES + api_settings.LOGIN_URL

            self.logger.info('Auth URL: {}'.format(url))

            payload = {
                'username': username,
                'password': encrypt_text(password),
                'grant_type': 'password',
                'client_id': client_id
            }
            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'client_id': client_id,
                'client_secret': client_secret,
            }
            self.logger.info('Calling authentication backend')

            start_date = time.time()
            auth_response = requests.post(url, params=payload, headers=headers, verify=settings.CERT)
            done = time.time()
            self.logger.info("Response time is {} sec.".format(done - start_date))
            json_data = auth_response.json()
            if auth_response.status_code == 200:
                access_token = json_data.get('access_token')
                correlation_id = json_data.get('correlation_id')

                if (access_token is not None) and (len(access_token) > 0):
                    self.logger.info('Checking user is exit in system')
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        self.logger.info("{} user was created".format(username))
                        user.is_staff = True
                        user.save()

                    self.logger.info("Adding access token for {} user name".format(username))
                    auth, created_token = Authentications.objects.get_or_create(user=user)
                    auth.access_token = access_token
                    auth.correlation_id = correlation_id
                    auth.save()

                    self.logger.info("Authentication success and generate session for {} user name".format(username))
                    self.logger.info('========== Finish authentication backend service ==========')
                    return user
                else:
                    self.logger.error("Cannot get access token from response of {} user name".format(username))
                    self.logger.info('========== Finish authentication backend service ==========')
                    return None
            else:
                if json_data.get('error_description') == 'Invalid credential':
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your username and password didn't match. Please try again."
                    )

        except Exception as ex:
            self.logger.error(ex)
            self.logger.error("{} user name authentication to backend was failed".format(username))
            self.logger.info('========== Finish authentication backend service ==========')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
