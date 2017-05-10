import datetime
import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "profile.html"
