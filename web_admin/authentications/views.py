from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
import requests, json


# from django.db.models import F, Count
#from django.template import loader

class InvalidUsernamePassword(Exception):
     pass

def validateLoginForm(username, password):

    if len(username) <= 0:
        raise InvalidUsernamePassword()

    if len(password) <= 0:
        raise InvalidUsernamePassword()


def form(request):
    # return HttpResponse("Hello, world. This is Login form.")
    return render(request, 'authentications/loginForm.html', {})

def doLogin(request):
    username = request.POST['username']
    password = request.POST['password']

    if request.user.is_authenticated:
        # Do something for authenticated user
        print('Redirect to a Main page.')
        return HttpResponseRedirect("/")


    else:
        # Do something for anonymous users.
        try:
            print('Validate params')
            validateLoginForm(username, password)

            # Prepare request
            clientId = 'J5LMCF6E3LH557FGP81B9AF3ABKM65H3'
            clientSecret = 'clientsecret_708141166013614699054496606232982517703465896176115'
            correlationId = 'abcxyz'

            # url = 'https://ascendcorp.com/api-gateway/system-user/v1/oauth/token'
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
            return render(request, 'authentications/loginForm.html', {
                'error_message': "Invalid Username or Password",
            })

        except requests.exceptions.Timeout:
            # Redisplay the login form.
            return render(request, 'authentications/loginForm.html', {
                'error_message': "Request was timeout.",
            })

        except requests.exceptions.TooManyRedirects:
            # Redisplay the login form.
            return render(request, 'authentications/loginForm.html', {
                'error_message': "Your URL was bad and try a different one",
            })

        except requests.exceptions.RequestException as e:
            # Redisplay the login form.
            return render(request, 'authentications/loginForm.html', {
                'error_message': "Error occurred. Try again!!!",
            })
        else:
            print('Assume request was succeeded')

            # Check user exists or not
            if not User.objects.filter(username=username).exists():
                print('Create new user')
                user = User.objects.create_user(username, None, password)
                user.save()

            print('authenticate user')
            user = authenticate(username=username, password=password)
            if user is not None:
                print('login user')
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect("/")

            else:
                # Return an 'invalid login' error message.
                # Redisplay the login form.
                return render(request, 'authentications/loginForm.html', {
                    'error_message': "Invalid Username or Password",
                })



def doLogout(request):
    logout(request)
    return HttpResponseRedirect("/")



