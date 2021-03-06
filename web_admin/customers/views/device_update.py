from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging

logger = logging.getLogger(__name__)


class MobileDeviceView(GroupRequiredMixin, TemplateView):
    group_required = "CAN_EDIT_CUSTOMER_CHANNEL_DETAILS"
    template_name = "device_update.html"
    raise_exception = False
    logger = logger
    login_url = 'web:permission_denied'


    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(MobileDeviceView, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get customer device detail ==========')
        context = super(MobileDeviceView, self).get_context_data(**kwargs)
        device_id = context['device_id']
        self.logger.info("Searching customer device with ID [{}]".format(device_id))
        url = api_settings.CUSTOMER_DEVICE_DETAIL_URL.format(device_id)
        is_success, status_code, data = RestFulClient.get(
            url,
            loggers=self.logger,
            headers=self._get_headers())
        if is_success:
            self.logger.info('Response_content: {}'.format(data))
            context['form'] = data
            self.logger.info('========== Finish get customer device detail ==========')
            return context
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update customer device ==========')
        mobile_device_id = kwargs['device_id']
        customer_id = kwargs['customer_id']
        form = request.POST
        if form['channel_type_id'] == '1':
            params = {
                'channel_type_id': form['channel_type_id'],
                'channel_id': form['channel_id'],
                'device_name': form['device_name'],
                'device_model': form['device_model'],
                'device_unique_reference': form['device_unique_reference'],
                'os': form['os'],
                'os_version': form['os_version'],
                'display_size_in_inches': form['display_size_in_inches'],
                'pixel_counts': form['pixel_counts'],
                'unique_number': form['unique_number'],
                'mac_address': form['mac_address'],
                'serial_number': form['serial_number'],
                'network_provider_name': form['network_provider_name'],
                'public_ip_address': form['public_ip_address'],
                'app_version': form['app_version'],
                'supporting_file_1': form['supporting_file_1'],
                'supporting_file_2': form['supporting_file_2']
            }

        elif form['channel_type_id'] == '2':
            params = {
                'channel_type_id': form['channel_type_id'],
                'channel_id': form['channel_id'],
                'mac_address': form['mac_address'],
                'network_provider_name': form['network_provider_name'],
                'public_ip_address': form['public_ip_address'],
                'supporting_file_1': form['supporting_file_1'],
                'supporting_file_2': form['supporting_file_2']
            }

        url = api_settings.CUSTOMER_UPDATE_DEVICE_URL.format(mobile_device_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params)
        self.logger.info("Params: {} ".format(params))
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            self.logger.info('========== Finish update customer device ==========')
            return redirect('customers:customer_management_summary', customerId=customer_id)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                status_code == 'invalid_access_token'):
            raise InvalidAccessToken(status_message)
