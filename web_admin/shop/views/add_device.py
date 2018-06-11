import logging

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from shop.utils import get_channel_detail
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient

from web_admin import api_settings
from web_admin import setup_logger

logger = logging.getLogger(__name__)


class AddDeviceView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_EDIT_AGENT_CHANNEL_DETAILS"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddDeviceView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        shop_id = int(kwargs['shop_id'])
        url = api_settings.ADD_AGENT_DEVICE
        self.logger.info('========== Start add device ==========')
        channel_id = request.POST["channel_id"]
        channel_type = get_channel_detail(self, channel_id)
        params = {
            "channel_type_id": channel_type['channel_type_id'],
            "channel_id": channel_id,
            "shop_id": shop_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                       headers=self._get_headers(),
                                                                       params=params,
                                                                       loggers=self.logger)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish add shop ==========')
        if is_success:
            messages.success(request, 'Add device successfully')
        else:
            messages.success(request, 'Add device successfully')

        return redirect('shop:shop_edit', id=shop_id)
