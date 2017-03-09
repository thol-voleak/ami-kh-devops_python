from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Authentications
import logging

logger = logging.getLogger(__name__)


def logout_user(request):
    logger.info("{} username start logging out".format(request.user))
    if request.user.is_authenticated:
        auth = Authentications.objects.get(user=request.user)
        if auth is not None:
            logger.info('Deleting current session info')
            auth.delete()

    logout(request)
    logger.info("{} username was logout".format(request.user))
    return redirect('/admin-portal/')
