import logging
import random
import string
import time
import requests

from django.conf import settings
from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken

from authentications.models import *

logger = logging.getLogger(__name__)


class DetailView(TemplateView):
    template_name = "clients/client_detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting client detail ==========')

            context = super(DetailView, self).get_context_data(**kwargs)
            client_id = context['client_id']
            logger.info('========== Finished getting client detail ==========')

            return self._get_client_detail(client_id)
        except:
            context = {'client_info': {},
                       'error_msg': 'Sorry, we cannot get client detail.'}
            return context

    def _get_client_detail(self, client_id):

        url = settings.CLIENTS_LIST_URL + '/' + client_id
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        try:
            auth = Authentications.objects.get(user=self.request.user)
            access_token = auth.access_token
        except Exception as e:
            raise InvalidAccessToken("{}".format(e))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer ' + access_token,
        }

        logger.info('Getting client detail from backend')
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        logger.info("Get client url: {}".format(url))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        if response_json['status']['code'] == "success":
            logger.info("Client detail was fetched.")
            data = response_json.get('data')
            context = {'client_info': data,
                       'error_msg': None}
            return context

        if response_json["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["message"])
