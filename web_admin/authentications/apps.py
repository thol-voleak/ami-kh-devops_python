from django.apps import AppConfig
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
            print('Validate params')
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
            # request = requests.post(url, data=json.dumps(payload), headers=headers)
            request = requests.post(url, data=payload, headers=headers)

            """TODO Check response success or fail
            #TODO User exiting in our system?
            Check user first if already have should get from command --- user, created = User.objects.get_or_create()
            """
            user = User(username=username)
            user.is_staff = True
            user.save()
            return user

        except InvalidUsernamePassword:
            # Redisplay the login form.
            print('InvalidUsernamePassword')
            return render(request, 'web:login.html', {
                'error_message': "Invalid Username or Password",
            })

        except requests.exceptions.Timeout:
            # Redisplay the login form.
            print('Timeout')
            return render(request, 'web:login.html', {
                'error_message': "Request was timeout.",
            })

        except requests.exceptions.TooManyRedirects:
            # Redisplay the login form.
            print('TooManyRedirects')
            return render(request, 'web:login.html', {
                'error_message': "Your URL was bad and try a different one",
            })

        except requests.exceptions.RequestException as e:
            # Redisplay the login form.
            print('RequestException')
            return render(request, 'web:login.html', {
                'error_message': "Error occurred. Try again!!!",
            })
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
