from django.apps import AppConfig
from django.contrib.auth.models import User
from django.conf import settings

import requests, json
import logging

logger = logging.getLogger(__name__)


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class InvalidUsernamePassword(Exception):
    pass


class CustomBackend:
    def validateLoginForm(self, username, password):
        if len(username) == 0:
            raise InvalidUsernamePassword()

        if len(password) == 0:
            raise InvalidUsernamePassword()

    def authenticate(self, username=None, password=None):
        try:
            logger.info('Validate params')
            self.validateLoginForm(username, password)

            client_id = settings.CLIENTID
            client_secret = settings.CLIENTSECRET
            url = settings.LOGIN_URL

            #TODO Generate or Random string for correlation id
            correlation_id = "asdfasdfasdf"

            payload = {'username': username,
                       'password': password,
                       'grant_type': 'password',
                       'client_id': client_id}

            headers = {'content-type': 'application/x-www-form-urlencoded',
                       'correlation-id': correlation_id,
                       'client_id': client_id,
                       'client_secret': client_secret,
                       }

            logger.info('Call authentication api gateway')
            auth_request = requests.post(url, params=payload, headers=headers)
            logger.info("response {}".format(auth_request.content))
            logger.info('Check response success or fail')
            json_data = auth_request.json()
            access_token = json_data.get('access_token')
            if (access_token is not None) and (len(access_token) > 0):
                logger.info('Check if User exists in our system?')
                user, created = User.objects.get_or_create(username=username)
                if created:
                    logger.info('user was created')
                    user = User(username=username)
                    user.is_staff = True
                    user.save()
                    return user
                else:
                    logger.info('user was retrieved')
                    return user

            else:
                logger.info('Invalid access token')
                return None

        except InvalidUsernamePassword:
            logger.info('InvalidUsernamePassword')
            return None

        except ValueError:
            logger.info('No JSON object could be decoded.')
            return None

        except requests.exceptions.Timeout:
            logger.info('Timeout')
            return None

        except requests.exceptions.TooManyRedirects:
            logger.info('TooManyRedirects')
            return None

        except requests.exceptions.RequestException as e:
            logger.info('RequestException')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
