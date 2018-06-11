from braces.views import GroupRequiredMixin
from web_admin import setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import CUSTOMER_DEVICE_LIST_URL
from web_admin.get_header_mixins import GetHeaderMixin
from customers.utils import check_permission_customer_management, get_supported_channels, get_channel_permissions_list
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class CustomerManagementSummary(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "management_summary.html"
    group_required = "CAN_VIEW_CUSTOMER_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CustomerManagementSummary, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        context = super(CustomerManagementSummary, self).get_context_data(**kwargs)
        customerId = int(context['customerId'])

        permissions = check_permission_customer_management(self)
        if not permissions['CAN_VIEW_CUSTOMER_MANAGEMENT']:
            if permissions['CAN_ACCESS_CUSTOMER_DEVICE_TAB']:
                return redirect('customers:customer_management_device', customerId=int(context['customerId']))

        context.update(
            {'customerId': customerId,
             'permissions': permissions
             })

        if permissions['CAN_ACCESS_CUSTOMER_DEVICE_TAB']:
            self.logger.info('========== Start getting Devices list ==========')
            data, success, status_message = self._get_devices(customerId)
            if success:
                devices_list = data.get("devices", [])
                page = data.get("page", {})
                summary_device_list = list(devices_list)
                if len(devices_list) > 5:
                    summary_device_list = devices_list[:5]

                supported_channels = get_supported_channels(self)
                access_channel_permissions = get_channel_permissions_list(self, customerId)

                dict_channels = {int(x['id']): x for x in supported_channels}
                id_channels_permissions = {int(x['channel']['id']) for x in access_channel_permissions}
                for id, channel in dict_channels.items():
                    if id in id_channels_permissions:
                        channel['grant_permission'] = True
                    else:
                        channel['grant_permission'] = False

                supported_channels = dict_channels.values()

                context.update(
                    {'total_result': page.get('total_elements', 0),
                     'summary_device_list': summary_device_list,
                     'supported_channels': supported_channels
                     })
            elif (status_message == "access_token_expire") or (status_message == 'authentication_fail') or (
                        status_message == 'invalid_access_token'):
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)

            self.logger.info('========== Finish getting Devices list ==========')
        return render(request, self.template_name, context)

    def _get_devices(self, customerId):
        body = {}
        body['customer_id'] = customerId
        body['is_deleted'] = False

        api_path = CUSTOMER_DEVICE_LIST_URL
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('devices', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message