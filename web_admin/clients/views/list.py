from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "clients/clients_list.html"
    logger = logger

    group_required = "CAN_LIST_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Getting client list ==========")
        data = self.get_clients_list()

        permissions = {}
        permissions['is_perm_client_create'] = check_permissions_by_user(self.request.user, "CAN_CREATE_CLIENTS")
        permissions['is_perm_client_update'] = check_permissions_by_user(self.request.user, "CAN_UPDATE_CLIENTS")
        permissions['is_perm_client_generate'] = check_permissions_by_user(self.request.user, "CAN_REGENERATE_CLIENTS")
        permissions['is_perm_client_delete'] = check_permissions_by_user(self.request.user, "CAN_DELETE_CLIENTS")
        permissions['is_perm_client_suspend'] = check_permissions_by_user(self.request.user, "CAN_SUSPEND_CLIENTS")
        permissions['is_perm_client_change_scope'] = check_permissions_by_user(self.request.user, "CAN_CHANGE_SCOPES_CLIENTS")

        result = {'data': data,
                  'permissions': permissions,
                  'msg': self.request.session.pop('client_update_msg', None),
                  'add_client_msg': self.request.session.pop('add_client_msg', None)}
        self.logger.info("========== Finish Getting client list ==========")
        return result

    def get_clients_list(self):
        url = api_settings.CLIENTS_LIST_URL
        data, success = self._get_method(url, 'Client List', logger, True)
        if success:
            return data
        else:
            return []
