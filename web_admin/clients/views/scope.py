from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.contrib import messages
from django.shortcuts import redirect
from web_admin.mixins import GetChoicesMixin
from web_admin.restful_methods import RESTfulMethods
import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class ScopeList(GroupRequiredMixin, TemplateView, GetChoicesMixin, RESTfulMethods):
    template_name = "clients/client_scope.html"
    logger = logger

    group_required = "CAN_CHANGE_SCOPES_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ScopeList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start Updating client scopes ==========")
        context = super(ScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']

        update_scopes = request.POST.getlist('scope')
        update_scopes = [int(i) for i in update_scopes]
        granted_scopes = request.session.get('client_scopes', [])
        granted_scope_ids = [scope.get('id') for scope in granted_scopes]

        self.update_scopes(request, client_id, granted_scope_ids, update_scopes)
        self.logger.info("========== Finish Updating client scopes ==========")

        return redirect(request.META['HTTP_REFERER'])

    def update_scopes(self, request, client_id, granted_scope, update_scopes):
        scopes_to_delete = [scope for scope in granted_scope if scope not in update_scopes]
        scopes_to_insert = [scope for scope in update_scopes if scope not in granted_scope]

        url = api_settings.CLIENT_SCOPES.format(client_id=client_id)

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
        params = {"scopes":scopes}

        data, success = self._post_method(url, 'Client Scopes', logger, params)
        return success

    def delete_scopes(self, url, scopes):
        if not scopes:
            return True
        params = {"scopes": scopes}
        data, success = self._delete_method(url, 'Client Scopes', logger, params)
        return success

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Getting client scopes ==========")
        context = super(ScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']
        all_scopes = self._get_all_scopes_list()
        client_scopes = self._get_client_scopes(client_id)

        self.request.session['client_scopes'] = client_scopes

        all_scopes = self.update_granted_scopes_for_all_scopes(all_scopes,client_scopes)
        context['all_scopes'] = all_scopes
        self.logger.info("========== Finish Getting client scopes ==========")
        return context

    def _get_all_scopes_list(self):
        url = api_settings.ALL_SCOPES_LIST_URL
        data, success = self._get_method(url, 'Client Scopes', logger, True)

        if success:
            return data.get('apis', [])
        return []

    def _get_client_scopes(self, client_id):
        url = api_settings.CLIENT_SCOPES.format(client_id=client_id)
        data, success = self._get_method(url, 'Client Scopes', logger, True)

        if success:
            return data.get('scopes', [])
        return []

    def update_granted_scopes_for_all_scopes(self, all_scopes, client_scopes ):
        client_scopes_id = [x['id'] for x in client_scopes]
        for x in all_scopes:
            if x['id'] in client_scopes_id:
                x['is_granted'] = True
            else:
                x['is_granted'] = False
        return all_scopes
