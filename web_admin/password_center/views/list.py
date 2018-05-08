from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "password_center/password_center_list.html"
    logger = logger

    group_required = "CAN_MANAGE_PASSWORD_CENTER"
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
        self.logger.info("========== Start getting password center identity type list ==========")
        data = self.get_identity_types_list()
        result = {'data': data }
        self.logger.info("========== Finish getting  password center identity type list ==========")
        return result

    def get_identity_types_list(self):
        body = {}
        data, success, status_message = self._get_identity_types_list(params=body)
        if success:
            return data
        else:
            return []


    def _get_identity_types_list(self, params):
        self.logger.info('========== Start searching password center identity type  ==========')

        api_path = api_settings.PASSWORD_CENTER_IDENTITY_TYPE_URL
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=params, response=data.get('password center identity type', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message
