from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.contrib import messages
from django.shortcuts import redirect
from web_admin.mixins import GetChoicesMixin
from web_admin.utils import build_logger
from web_admin.restful_helper import RestfulHelper
from channel_gateway.api.utils  import get_api_list
import logging


class ClientChannelGatewayScopeList(TemplateView, GetChoicesMixin):
    template_name = "clients/client_channel_gateway_scope.html"
    logger = logging.getLogger(__name__)

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(request, __name__)
        return super(ClientChannelGatewayScopeList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start Updating client scopes ==========")
        context = super(ClientChannelGatewayScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']
        self.logger.info("========== Finish Updating client scopes ==========")

        return redirect(request.META['HTTP_REFERER'])

    def get_context_data(self, **kwargs):
        context = super(ClientChannelGatewayScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']
        body_req = {
            'is_deleted': False,
            'paging': False
        }
        all_apis = get_api_list(self, body_req).get('apis')
        client_channel_gw_scopes = self._get_all_channel_gateway_scopes_list(client_id)

        all_apis = self.update_api_list_with_selected_api_in_client_channel_scope_api(all_apis, client_channel_gw_scopes)
        context['all_apis'] = all_apis
        return context

    def update_api_list_with_selected_api_in_client_channel_scope_api(self, all_apis, client_channel_gw_scopes):
        extracted_api_id_list_from_client_channel_gw_scope = []
        if client_channel_gw_scopes:
            extracted_api_id_list_from_client_channel_gw_scope = [scope['api'].get('id') for scope in client_channel_gw_scopes]
        for api in all_apis:
            if api['id'] in extracted_api_id_list_from_client_channel_gw_scope:
                api['is_checked'] = True
            else:
                api['is_checked'] = False
        return all_apis

    def _get_all_channel_gateway_scopes_list(self, client_id):
        api_path = api_settings.GET_CLIENT_CHANNEL_GATEWAY_SCOPE_LIST_API.format(client_id=client_id)

        success, status_code, status_message, data = RestfulHelper.send("GET", api_path, {}, self.request, "getting client channel gateway scopes", "data.scopes")
        if data is None:
            data = {}
            data['scopes'] = []
        return data['scopes']
