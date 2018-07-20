from authentications.apps import InvalidAccessToken
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
import logging


logger = logging.getLogger(__name__)


class BlockedDevicesList(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "blocked_devices.html"
    logger = logger

    group_required = "CAN_MANAGE_BLOCKED_DEVICES"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BlockedDevicesList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Blocked Devices page ==========')
        context = super(BlockedDevicesList, self).get_context_data(**kwargs)
        param = {}
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_TICKET,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=param)

        if is_success:
            self.logger.info("Response_content_count:{}".format(len(data)))
            context['devices'] = [i for i in data.get('tickets') if i['is_deleted'] == False]
            context['can_unblock_device'] = self.check_membership(['CAN_DELETE_FRAUD_TICKET'])
            device_count = 0
            for ticket in context['devices']:
                if ticket['action'] == 'register customer':
                    device_count += 1
            context['total_devices'] = device_count
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        self.logger.info('========== Finished showing Blocked Devices page ==========')
        return context

