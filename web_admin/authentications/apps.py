from django.apps import AppConfig
from django.contrib.auth.models import User
import requests, json


class AuthenticationsConfig(AppConfig):
    name = 'authentications'

class InvalidUsernamePassword(Exception):
    pass

class MyCustomBackend:

    def validateLoginForm(self, username, password):
        if len(username) <= 0:
            raise InvalidUsernamePassword()

        if len(password) <= 0:
            raise InvalidUsernamePassword()


    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):
        # import pdb;
        # pdb.set_trace()

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

            print('Call authen API')
            # request = requests.post(url, data=json.dumps(payload), headers=headers)
            request = requests.post(url, data=payload, headers=headers)


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
            print('Assume request was succeeded')

            try:
                # Try to find a user matching your username
                #
                # #  Check the password is the reverse of the username
                # if password == username[::-1]:
                #     # Yes? return the Django user object
                #     return user
                # else:
                #     # No? return None - triggers default login failed
                user = User(username=username)
                user.is_staff = True
                user.save()
                return user
            except User.DoesNotExist:
                # No user was found, return None - triggers default login failed
                return None




    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


    def _login_valid(username, password):
        pass
