from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.contrib import messages
from django.shortcuts import redirect
from web_admin.mixins import GetChoicesMixin
from web_admin.utils import build_logger, check_permissions
from web_admin.restful_helper import RestfulHelper
from channel_gateway.api.utils  import get_api_list
import logging


class ClientChannelGatewayScopeList(TemplateView, GetChoicesMixin):
    template_name = "clients/client_channel_gateway_scope.html"
    logger = logging.getLogger(__name__)

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, 'CAN_CHANGE_SCOPES_CHANNEL_GW_CLIENTS')
        self.logger = build_logger(request, __name__)
        return super(ClientChannelGatewayScopeList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = super(ClientChannelGatewayScopeList, self).get_context_data(**kwargs)
        client_id = context['client_id']
        old_selected_api_id_list = request.POST.getlist('old_selected_api_id_list')
        new_selected_api_id_list = request.POST.getlist('channel_gw_scope')

        #convert string list to int list
        old_selected_api_id_list = list(map(int, old_selected_api_id_list))
        new_selected_api_id_list = list(map(int, new_selected_api_id_list))

        added_api_list = [id for id in new_selected_api_id_list if id not in old_selected_api_id_list]
        removed_api_list = [id for id in old_selected_api_id_list if id not in new_selected_api_id_list]

        add_body_req = {
            'scopes': added_api_list
        }

        delete_body_req = {
            'scopes': removed_api_list
        }
        is_add_success = True
        is_delete_success = True

        if added_api_list:
            is_add_success = self.add_client_channel_scope(add_body_req, client_id)
        if removed_api_list:
            is_delete_success = self.delete_client_channel_scope(delete_body_req, client_id)

        if is_add_success and is_delete_success and (added_api_list or removed_api_list):
            messages.success(request, 'Updated data successfully')

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
        if client_channel_gw_scopes:
            client_channel_gw_scopes = [scope for scope in client_channel_gw_scopes if not scope.get('is_deleted')]

        all_apis, selected_api_id_list = self.update_api_list_with_selected_api_in_client_channel_scope_api(all_apis, client_channel_gw_scopes)
        context.update({
            'all_apis': all_apis,
            'selected_api_id_list': selected_api_id_list
        })
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
        return all_apis, extracted_api_id_list_from_client_channel_gw_scope

    def _get_all_channel_gateway_scopes_list(self, client_id):
        api_path = api_settings.GET_CLIENT_CHANNEL_GATEWAY_SCOPE_LIST_API.format(client_id=client_id)

        success, status_code, status_message, data = RestfulHelper.send("GET", api_path, {}, self.request, "getting client channel gateway scopes", "data.scopes")
        if data is None:
            data = {}
            data['scopes'] = []
        return data['scopes']

    def add_client_channel_scope(self, params, client_id):
        api_path = api_settings.GET_CLIENT_CHANNEL_GATEWAY_SCOPE_LIST_API.format(client_id=client_id)

        success, status_code, status_message, data = RestfulHelper.send("POST", api_path, params, self.request, "adding client channel gateway scopes")
        return success

    def delete_client_channel_scope(self, params, client_id):
        api_path = api_settings.GET_CLIENT_CHANNEL_GATEWAY_SCOPE_LIST_API.format(client_id=client_id)

        success, status_code, status_message, data = RestfulHelper.send("DELETE", api_path, params, self.request,
                                                                        "deleting client channel gateway scopes")
        return success

