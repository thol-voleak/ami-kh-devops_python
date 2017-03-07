from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import Authentications
import logging

logger = logging.getLogger(__name__)

def logout_user(request):

    logger.info('Logging out user')
    if request.user.is_authenticated:
        # Do something for authenticated users.
        auth = Authentications.objects.get(user=request.user)
        if auth is not None:
            auth.delete()

    logout(request)
    return redirect('/admin-portal/')
