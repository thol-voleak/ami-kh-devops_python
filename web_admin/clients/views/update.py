import logging

from braces.views import GroupRequiredMixin

from web_admin import api_settings, setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class ClientUpdateForm(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "clients/update_client_form.html"
    logger = logger

    group_required = "CAN_UPDATE_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ClientUpdateForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Updating client detail ==========")
        context = super(ClientUpdateForm, self).get_context_data(**kwargs)
        client_id = context['client_id']
        return self._get_client_detail(client_id)

    def _get_client_detail(self, client_id):

        url = api_settings.CLIENTS_LIST_URL + '/' + client_id
        data, success = self._get_method(url, 'Client Detail', logger)

        context = {'client_info': data,
                   'error_msg': None}
        return context


class ClientUpdate(TemplateView, RESTfulMethods):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ClientUpdate, self).dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):

        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": request.POST.get('client_name'),
            "scope": request.POST.get('scope'),
            "authorized_grant_types": request.POST.get('authorized_grant_types'),
            "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
            "authorities": "",
            "access_token_validity": request.POST.get('access_token_validity'),
            "refresh_token_validity": request.POST.get('refresh_token_validity'),
            "authorization_code_validity": request.POST.get('authorization_code_validity'),
            "additional_information": "",
            "resource_ids": "",
            "autoapprove": ""
        }

        url = api_settings.UPDATE_CLIENT_URL.format(client_id)

        data, success = self._put_method(url, 'client', logger, params)
        self.logger.info("========== Finish Updating client detail ==========")

        if success:
            request.session['client_update_msg'] = 'Updated data successfully'
            return redirect('clients:client-list')
        else:
            context = {'client_info': params,
                       'error_msg': data}
            return render(request, 'clients/update_client_form.html', context)
