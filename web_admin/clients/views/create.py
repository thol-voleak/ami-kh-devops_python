import logging
import random
import string

from braces.views import GroupRequiredMixin

from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class ClientCreate(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = 'clients/create_client_form.html'
    logger = logger

    group_required = "CAN_CREATE_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ClientCreate, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info("========== Start Creating client ==========")
        client_id = _generate_client_id()
        client_secret = _generate_client_secret()

        client_info = {
            "client_id": client_id,
            "client_secret": client_secret,
            "authorized_grant_types": None,
            "access_token_validity": None,
            "refresh_token_validity": None,
            "authorization_code_validity": None
        }

        context = {
            'client_info': client_info,
            'error_msg': None
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

        url = api_settings.CREATE_CLIENT_URL

        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": request.POST.get('client_name'),
            "scope": "",
            "authorized_grant_types": request.POST.get('authorized_grant_types'),
            "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
            "authorities": "",
            "access_token_validity": request.POST.get('access_token_validity'),
            "refresh_token_validity": request.POST.get('refresh_token_validity'),
            "authorization_code_validity": request.POST.get('authorization_code_validity')
        }

        data, success = self._post_method(url, 'client', logger, params)

        self.logger.info("========== Finish Creating client ==========")
        if success:
            self.request.session['add_client_msg'] = "Added client successfully"
            return redirect('clients:client-list')
        else:
            client_info = {
                "client_id": client_id,
                "client_secret": client_secret,
                "client_name": request.POST.get('client_name'),
                "scope": "",
                "authorized_grant_types": request.POST.get('authorized_grant_types'),
                "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
                "authorities": "",
                "access_token_validity": request.POST.get('access_token_validity'),
                "refresh_token_validity": request.POST.get('refresh_token_validity'),
                "authorization_code_validity": request.POST.get('authorization_code_validity')
            }
            context = {'client_info': client_info, 'error_msg': data}
            return render(request, self.template_name, context)


def _generate_client_id():
    client_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
    return client_id


def _generate_client_secret():
    client_secret = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
    return client_secret
