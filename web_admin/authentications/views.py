from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
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

def login(request):
    try:
        # Validate params
        username = request.POST['username']
        password = request.POST['password']

        validateLoginForm(username, password)

        # Prepare request
        url = 'https://api.github.com/some/endpoint'
        payload = {'username': 'abcxyz',
                   'password': 'secret123'}
        headers = {'content-type': 'application/json'}

        # Call authen API
        #request = requests.post(url, data=json.dumps(payload), headers=headers)
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
        return HttpResponseRedirect(reverse('authentications:welcome', args=('nothing',)))


def welcome(request):
    return HttpResponse("Welcome to Web Admin")