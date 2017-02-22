from django.apps import AppConfig
from django.contrib.auth.models import User


class AuthenticationsConfig(AppConfig):
    name = 'authentications'


class MyCustomBackend:

    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):
        # import pdb;
        # pdb.set_trace()
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
