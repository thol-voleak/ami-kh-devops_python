from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from django.contrib import messages
from django.shortcuts import redirect

from web_admin.mixins import GetChoicesMixin
from authentications.apps import InvalidAccessToken

import requests
import logging

logger = logging.getLogger(__name__)


class ScopeList(TemplateView, GetChoicesMixin):
    template_name = "clients/client_scope.html"

    def post(self, request, *args, **kwargs):

        context = super(ScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']

        logger.info('========== Start update Client Scopes ==========')

        update_scopes = request.POST.getlist('scope')
        update_scopes = [int(i) for i in update_scopes]
        granted_scopes = request.session.get('client_scopes', [])
        granted_scope_ids = [scope.get('id') for scope in granted_scopes]

        self.update_scopes(request, client_id, granted_scope_ids, update_scopes)
        logger.info('========== Finished updating Client Scopes ==========')

        return redirect(request.META['HTTP_REFERER'])

    def update_scopes(self, request, client_id, granted_scope, update_scopes):
        scopes_to_delete = [scope for scope in granted_scope if scope not in update_scopes]
        scopes_to_insert = [scope for scope in update_scopes if scope not in granted_scope]

        url = settings.CLIENT_SCOPES.format(client_id=client_id)

        delete_success = self.delete_scopes(url, scopes_to_delete)
        insert_success = self.insert_scopes(url, scopes_to_insert)

        if delete_success and insert_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )

    def insert_scopes(self, url, scopes):
        if not scopes:
            return True
        logger.info("Adding client scopes by user {}".format(self.request.user.username))
        logger.info("Add client scopes url: {}".format(url))
        data = {"scopes":scopes}
        logger.info("Add client scopes request body: {}".format(data))
        response = requests.post(url, headers=self._get_headers(), json=data, verify=False)
        logger.info("Add client scopes response content: {}".format(response.content))
        if response.status_code == 200:
            return True
        else:
            logger.info("Add client scopes received response with status {}".format(
                response.status_code))
            return False

    def delete_scopes(self, url, scopes):
        if not scopes:
            return True
        logger.info("Deleting client scopes by user {}".format(self.request.user.username))
        logger.info("Delete client scopes url: {}".format(url))
        data = {"scopes": scopes}
        logger.info("Delete client scopes request body: {}".format(data))
        response = requests.delete(url, headers=self._get_headers(), json=data, verify=False)
        logger.info("Delete client scopes response content: {}".format(response.content))
        if response.status_code == 200:
            return True
        else:
            logger.info("Delete client scopes received response with status {}".format(
                response.status_code))
            return False

    def get_context_data(self, **kwargs):

        context = super(ScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']

        logger.info('========== Start get All Scope List ==========')
        all_scopes = self._get_all_scopes_list()
        logger.info('========== Finished get All Scope List ==========')

        logger.info('========== Start getting client scopes ==========')
        client_scopes = self._get_client_scopes(client_id)
        logger.info('========== Finished getting client scopes ==========')

        self.request.session['client_scopes'] = client_scopes

        all_scopes = self.update_granted_scopes_for_all_scopes(all_scopes,client_scopes)
        context['all_scopes'] = all_scopes
        return context

    def _get_all_scopes_list(self):
        logger.info("Getting all scope list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)
        url = settings.ALL_SCOPES_LIST_URL
        logger.info("Getting all scope list url: {}".format(url))
        response = requests.get(url, headers=headers, verify=False)
        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
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
        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
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
