import logging

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from web_admin.mixins import GetChoicesMixin

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetChoicesMixin):
    template_name = "clients/client_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        client_id = context['client_id']

        logger.info('========== Start getting client detail ==========')
        client_info, success_info = self._get_client_detail(client_id)
        logger.info('========== Finished getting client detail ==========')

        logger.info('========== Start getting client scopes ==========')
        client_scopes, success_scope = self._get_client_scopes(client_id)
        logger.info('========== Finished getting client scopes ==========')

        context['client_info'] = client_info
        context['client_scopes'] = client_scopes
        return context

    def _get_client_scopes(self, client_id):
        logger.info("Getting client scopes by user: {}".format(self.request.user.username))
        url = settings.CLIENT_SCOPES.format(client_id)
        response = requests.get(url, headers=self._get_headers(), verify=False)
        logger.info("Get client scopes url: {}".format(url))
        logger.info("Received data with response status: {}".format(response.status_code))

        if response.status_code == 200:
            logger.info("Client scopes was fetched.")
            response_json = response.json()
            return response_json.get('data'), True
        return None, False

    def _get_client_detail(self, client_id):
        logger.info("Getting client detail by user: {}".format(self.request.user.username))

        url = settings.CLIENTS_LIST_URL + '/' + client_id
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        logger.info("Get client url: {}".format(url))
        logger.info("Received data with response status: {}".format(response.status_code))

        if response.status_code == 200:
            logger.info("Client detail was fetched.")
            response_json = response.json()
            return response_json.get('data'), True
        return None, False
