import logging
from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)


class SearchView(TemplateView):
    template_name = "system_user/system_user_list.html"

    def get(self, request):
        return render(request, 'system_user/system_user_list.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')

        body = {}
        if username is not '':
            body['username'] = username
        if email is not '':
            body['email'] = email

        search_url = settings.DOMAIN_NAMES + settings.SEARCH_SYSTEM_USER
        logger.info("Search system user with [{}] username and [{}] email".format(username, email))
        search_response = requests.post(search_url, headers=get_auth_header(self.request.user), json=body,
                                        verify=settings.CERT)
        logger.info('Got search result from backend with [{}] http status'.format(search_response.status_code))
        json_data = search_response.json()

        if search_response.status_code == 200 and json_data.get('status').get('code') == 'success':
            logger.info('Found [{}] system users'.format(len(search_response.json()['data'])))
            return render(request, 'system_user/system_user_list.html', {'data': json_data.get('data')})
        else:
            logger.info("Got error when search system user")
            raise Exception(search_response.content)
