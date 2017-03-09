from django.apps import AppConfig
from django.contrib.auth.models import User
from .models import Authentications
from django.conf import settings
import requests, json, random, string, logging
import time

logger = logging.getLogger(__name__)


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class InvalidUsernamePassword(Exception):
    pass


class CustomBackend:
    def __init__(self):
        pass

    def authenticate(self, username=None, password=None):
        try:
            logger.info('========== Start authentication backend service ==========')
            self._validateLoginForm(username, password)

            client_id = settings.CLIENTID
            client_secret = settings.CLIENTSECRET
            url = settings.LOGIN_URL

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
                'correlation-id': correlation_id,
                'client_id': client_id,
                'client_secret': client_secret,
            }

            logger.info('Calling authentication backend')
            # import ipdb;ipdb.set_trace()

            start_date = time.time()
            auth_request = requests.post(url, params=payload, headers=headers, verify=False)

            # import ipdb;ipdb.set_trace()
            done = time.time()
            logger.info("Response time is {} sec.".format(done-start_date))
            logger.info("Authentication response is {}".format(auth_request.status_code))

            json_data = auth_request.json()
            access_token = json_data.get('access_token')
            if (access_token is not None) and (len(access_token) > 0):

                logger.info('Checking user is exit in system')
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user = User(username=username)
                    user.is_staff = True
                    user.save()
                    logger.info('{} user was created', username)

                logger.info("Adding access token for {} user name".format(username))
                try:
                    auth = Authentications.objects.get(user=user)
                    auth.access_token = access_token
                    auth.save()
                except:
                    auth = Authentications(user=user, access_token=access_token)
                    auth.save()
                logger.info("Authentication success and geraneration session for {} user name".format(username))
                logger.info('========== Finish authentication backend service ==========')
                return user
            else:
                logger.error("Cannot get access token from response of {} user name".format(username))
                logger.info('========== Finish authentication backend service ==========')
                return None

        except:
            logger.error("{} user name authentication to backend was failed".format(username))
            logger.info('========== Finish authentication backend service ==========')
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _validateLoginForm(self, username, password):
        if len(username) == 0:
            raise InvalidUsernamePassword()

        if len(password) == 0:
            raise InvalidUsernamePassword()
