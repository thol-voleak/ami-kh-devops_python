from authentications.models import Authentications
from web_admin import api_settings, setup_logger

from django.apps import AppConfig
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib import messages
from web_admin import setup_logger, RestFulClient
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
            loggers = setup_logger(request, logger, request.user)
            loggers.info('========== Start authentication backend service ==========')
            client_id = settings.CLIENTID
            client_secret = settings.CLIENTSECRET
            url = settings.DOMAIN_NAMES + api_settings.LOGIN_URL

            loggers.info('Auth URL: {}'.format(url))

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
            loggers.info('Calling authentication backend')

            start_date = time.time()
            auth_response = requests.post(url, params=payload, headers=headers, verify=settings.CERT)

            done = time.time()
            loggers.info("Response time is {} sec.".format(done - start_date))
            json_data = auth_response.json()
            if auth_response.status_code == 200:
                access_token = json_data.get('access_token', None)
                correlation_id = json_data.get('correlation_id', None)

                if access_token != "" and access_token is not None:
                    loggers.info('Checking user is exit in system')
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        loggers.info("{} user was created".format(username))
                        user.is_staff = True
                        user.save()

                    user_profiles = self.get_user_profiles(request, username, access_token, correlation_id)
                    loggers.info("Adding access token for {} user name".format(username))

                    auth, created_token = Authentications.objects.get_or_create(user=user)
                    auth.access_token = access_token
                    auth.correlation_id = correlation_id
                    auth.system_user_id = user_profiles['id']
                    auth.username = user_profiles['username']
                    auth.firstname = user_profiles['firstname']
                    auth.lastname = user_profiles['lastname']
                    auth.email = user_profiles['email']
                    auth.mobile_number = user_profiles['mobile_number']
                    auth.is_deleted = bool(user_profiles['is_deleted'])
                    auth.created_timestamp = user_profiles['created_timestamp']
                    auth.last_updated_timestamp = user_profiles['last_updated_timestamp']
                    auth.save()
                    loggers.info("Authentication success and generate session for {} user name".format(username))

                    loggers.info('========== Finish authentication backend service ==========')
                    return user
                else:
                    loggers.error("Cannot get access token from response of {} user name".format(username))
                    loggers.info('========== Finish authentication backend service ==========')
                    return None
            else:
                if json_data.get('error_description') == 'Invalid credential':
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your username and password didn't match. Please try again."
                    )

        except Exception as ex:
            loggers.error(ex)
            loggers.error("{} user name authentication to backend was failed".format(username))
            loggers.info('========== Finish authentication backend service ==========')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_profiles(self, request, username, access_token, correlation_id):
        url = api_settings.SEARCH_SYSTEM_USER

        headers = {
            'content-type': 'application/json',
            'client_id': settings.CLIENTID,
            'correlation-id': correlation_id,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        params = {
            'username': username
        }

        is_success, status_code, status_message, data = RestFulClient.post(request=request, url=url, headers=headers,
                                                                           logger=logger, params=params)
        if is_success:
            return data[0]
