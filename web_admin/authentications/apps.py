from django.apps import AppConfig
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
import requests, json
import logging

logger = logging.getLogger(__name__)


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class InvalidUsernamePassword(Exception):
    pass


class MyCustomBackend:
    def validateLoginForm(self, username, password):
        if len(username) == 0:
            raise InvalidUsernamePassword()

        if len(password) == 0:
            raise InvalidUsernamePassword()

    def authenticate(self, username=None, password=None):
        try:
            logger.info('Validate params')
            self.validateLoginForm(username, password)

            # Prepare request
            clientId = 'J5LMCF6E3LH557FGP81B9AF3ABKM65H3'
            clientSecret = 'clientsecret_708141166013614699054496606232982517703465896176115'
            correlationId = 'abcxyz'

            # url = 'https://alp-eq-esg-01.tmn-dev.com:443/api-gateway/system-user/v1/oauth/token'
            url = 'https://github.com/KayEss/django-slumber'

            payload = {'username': username,
                       'password': password,
                       'grant_type': 'password',
                       'client_id': clientId}

            headers = {'content-type': 'application/x-www-form-urlencoded',  # application/json
                       'correlation-id': correlationId,
                       'client_id': clientId,
                       'client_secret': clientSecret,
                       }

            logger.info('Call authen API')

            """
                I'm not sure which line is the correct way to send a POST request. Could you consult me please!
            """
            # request = requests.post(url, data=json.dumps(payload), headers=headers)
            #authRequest = requests.post(url, data=payload, headers=headers)
            authRequest = requests.post(url, params=payload, headers=headers)

            logger.info('Check response success or fail')
            json = authRequest.json()
            accessToken = json.get('access_token')
            if (accessToken is not None) and (len(accessToken) > 0):
                # Succeeded
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
                # Failed
                # Redisplay the login form.
                logger.info('Invalid access token')
                return None

        except InvalidUsernamePassword:
            # Redisplay the login form.
            logger.info('InvalidUsernamePassword')
            return None

        except ValueError:
            logger.info('No JSON object could be decoded.')
            return None

        except requests.exceptions.Timeout:
            # Redisplay the login form.
            logger.info('Timeout')
            return None

        except requests.exceptions.TooManyRedirects:
            # Redisplay the login form.
            logger.info('TooManyRedirects')
            return None

        except requests.exceptions.RequestException as e:
            # Redisplay the login form.
            logger.info('RequestException')
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
