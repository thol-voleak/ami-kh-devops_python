import logging

from braces.views import GroupRequiredMixin

from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "clients/client_detail.html"
    logger = logger

    group_required = "CAN_DETAIL_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Getting client detail ==========")
        context = super(DetailView, self).get_context_data(**kwargs)
        client_id = context['client_id']

        client_info, success_info = self._get_client_detail(client_id)

        client_scopes, success_scope = self._get_client_scopes(client_id)
        context['client_info'] = client_info
        context['client_scopes'] = client_scopes
        self.logger.info("========== Finish Getting client detail ==========")
        return context

    def _get_client_scopes(self, client_id):
        url = api_settings.CLIENT_SCOPES.format(client_id=client_id)
        return self._get_method(url, 'client scopes', logger)

    def _get_client_detail(self, client_id):
        url = api_settings.CLIENTS_LIST_URL + '/' + client_id
        return self._get_method(url, 'client detail', logger)
