from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import setup_logger
from web_admin.api_settings import SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_MANAGE_SERVICE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "services/services_list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = self.get_services_list()

        permissions = {}
        permissions['CAN_VIEW_SERVICE'] = check_permissions_by_user(self.request.user, 'CAN_VIEW_SERVICE')
        permissions['CAN_EDIT_SERVICE'] = check_permissions_by_user(self.request.user, 'CAN_EDIT_SERVICE')
        permissions['CAN_EDIT_COMMAND_SERVICE'] = check_permissions_by_user(self.request.user, 'CAN_EDIT_COMMAND_SERVICE')
        permissions['CAN_DELETE_SERVICE'] = check_permissions_by_user(self.request.user, 'CAN_DELETE_SERVICE')
        permissions['CAN_ADD_SERVICE'] = check_permissions_by_user(self.request.user, 'CAN_ADD_SERVICE')

        result = {'data': data,
                  'permissions': permissions}
        return result

    def get_services_list(self):
        url = SERVICE_LIST_URL
        data, success = self._get_method(api_path=url, func_description="service list", is_getting_list=True)
        return data
