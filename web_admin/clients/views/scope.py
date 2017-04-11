from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header

from web_admin.mixins import GetChoicesMixin

import requests
import logging

logger = logging.getLogger(__name__)


class ScopeList(TemplateView, GetChoicesMixin):
    template_name = "clients/client_scope.html"

    def get_context_data(self, **kwargs):

        context = super(ScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']

        logger.info('========== Start get All Scope List ==========')
        all_scopes = self._get_all_scopes_list()
        logger.info('========== Finished get All Scope List ==========')

        logger.info('========== Start getting client scopes ==========')
        client_scopes = self._get_client_scopes(client_id)
        logger.info('========== Finished getting client scopes ==========')

        all_scopes = self.update_granted_scopes_for_all_scopes(all_scopes,client_scopes)
        context['all_scopes'] = all_scopes
        return context

    def _get_all_scopes_list(self):
        logger.info("Getting all scope list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)
        url = settings.ALL_SCOPES_LIST_URL
        logger.info("Getting all scope list url: {}".format(url))
        response = requests.get(url, headers=headers, verify=False)
        logger.info("Get all scopes url: {}".format(url))
        logger.info("Received data with response status: {}".format(response.status_code))

        if response.status_code == 200:
            response_json = response.json()
            apis = response_json.get('data').get('apis', [])
            logger.info('Total count of all scopes is {}'.format(len(apis)))
            return apis
        return []

    def _get_client_scopes(self, client_id):
        url = settings.CLIENT_SCOPES.format(client_id=client_id)
        response = requests.get(url, headers=self._get_headers(), verify=False)
        logger.info("Get client scopes url: {}".format(url))
        logger.info("Received data with response status: {}".format(response.status_code))

        if response.status_code == 200:
            response_json = response.json()
            client_scopes = response_json.get('data').get('scopes', [])
            logger.info('Total count of  scopes is {}'.format(len(client_scopes)))
            return client_scopes
        return []

    def update_granted_scopes_for_all_scopes(self, all_scopes, client_scopes ):
        client_scopes_id = [x['id'] for x in client_scopes]
        for x in all_scopes:
            if x['id'] in client_scopes_id:
                x['is_granted'] = True
            else:
                x['is_granted'] = False
        return all_scopes



