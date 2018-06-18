from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from web_admin.utils import get_back_url
from django.urls import reverse
import logging

from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class DeviceUpdateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_EDIT_AGENT_CHANNEL_DETAILS"
    template_name = "shop/device_update.html"
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
        return super(DeviceUpdateView, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get agent device detail ==========')
        context = super(DeviceUpdateView, self).get_context_data(**kwargs)
        device_id = context['device_id']
        self.logger.info("Searching agent device with ID [{}]".format(device_id))
        url = api_settings.AGENT_DEVICE_URL.format(device_id)
        is_success, status_code, data = RestFulClient.get(
            url,
            loggers=self.logger,
            headers=self._get_headers())
        if is_success:
            self.logger.info('Response_content: {}'.format(data))
            context['form'] = data
            context['shopId'] = context['id']
            self.logger.info('========== Finish get agent device detail ==========')
            return context
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update agent device ==========')
        edc_device_id = kwargs['device_id']
        shop_id = kwargs['id']
        form = request.POST
        if form['channel_type_id'] == '3':
            params = {
                'channel_type_id': form['channel_type_id'],
                'channel_id': form['channel_id'],
                'edc_serial_number': form['edc_serial_number'],
                'edc_model': form['edc_model'],
                'edc_software_version': form['edc_software_version'],
                'edc_firmware_version': form['edc_firmware_version'],
                'edc_sim_card_number': form['edc_sim_card_number'],
                'edc_battery_serial_number': form['edc_battery_serial_number'],
                'edc_adapter_serial_number': form['edc_adapter_serial_number'],
                'edc_smartcard_1_number': form['edc_smartcard_1_number'],
                'edc_smartcard_2_number': form['edc_smartcard_2_number'],
                'edc_smartcard_3_number': form['edc_smartcard_3_number'],
                'edc_smartcard_4_number': form['edc_smartcard_4_number'],
                'edc_smartcard_5_number': form['edc_smartcard_5_number'],
                'mac_address': form['mac_address'],
                'network_provider_name': form['network_provider_name'],
                'public_ip_address': form['public_ip_address'],
                'supporting_file_1': form['supporting_file_1'],
                'supporting_file_2': form['supporting_file_2']
            }
        elif form['channel_type_id'] == '4':
            params = {
                'channel_type_id': form['channel_type_id'],
                'channel_id': form['channel_id'],
                'pos_serial_number': form['pos_serial_number'],
                'pos_model': form['pos_model'],
                'pos_software_version': form['pos_software_version'],
                'pos_firmware_version': form['pos_firmware_version'],
                'pos_smartcard_1_number': form['pos_smartcard_1_number'],
                'pos_smartcard_2_number': form['pos_smartcard_2_number'],
                'pos_smartcard_3_number': form['pos_smartcard_3_number'],
                'pos_smartcard_4_number': form['pos_smartcard_4_number'],
                'pos_smartcard_5_number': form['pos_smartcard_5_number'],
                'mac_address': form['mac_address'],
                'network_provider_name': form['network_provider_name'],
                'public_ip_address': form['public_ip_address'],
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
        else:
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
        url = api_settings.AGENT_DEVICE_URL.format(edc_device_id)
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
            self.logger.info('========== Finish update agent device ==========')
            return redirect('shop:shop_edit', id=shop_id)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                status_code == 'invalid_access_token'):
            raise InvalidAccessToken(status_message)
