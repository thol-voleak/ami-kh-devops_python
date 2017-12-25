from web_admin import api_settings, setup_logger, RestFulClient
from authentications.utils import get_correlation_id_from_username
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class SPIView(TemplateView, GetHeaderMixin):
    template_name = 'services/spi/list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        if not service_command_id or not service_id or not command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url_option = request.POST.get('spi_url_option')
        spi_url_value_internal = request.POST.get('spi_url_value_internal')
        spi_url_value_external = request.POST.get('spi_url_value_external')
        spi_url_call_method = request.POST.get('spi_url_call_method')
        connection_timeout = request.POST.get('connection_timeout', 0)
        read_timeout = request.POST.get('read_timeout', 0)
        max_retry = request.POST.get('max_retry', 0)
        retry_delay = request.POST.get('retry_delay', 0)
        expire_in_minute = request.POST.get('expire_in_minute', 0)

        if spi_url_option == 'internal':
            spi_url = spi_url_value_internal
        elif spi_url_option == 'external':
            spi_url = spi_url_value_external

        if spi_url != "" and spi_url is not None:
            params = {
                "spi_url_type": spi_type,
                "url": spi_url,
                "spi_url_call_method": spi_url_call_method,
                "expire_in_minute": 0 if expire_in_minute == "" else int(expire_in_minute),
                "max_retry": 0 if max_retry == "" else int(max_retry),
                "retry_delay_millisecond": 0 if retry_delay == "" else int(retry_delay),
                "read_timeout": 0 if read_timeout == "" else int(read_timeout),
                "connection_timeout": 0 if connection_timeout == "" else int(connection_timeout)
            }
            success, status_code, message, data = self.add_spi(service_command_id, params)

            if success:
                message_level = messages.SUCCESS
                message_text = 'Added SPI URL successfully'
            elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)
            else:
                message_level = messages.ERROR
                message_text = message
        else:
            message_level = messages.ERROR
            message_text = "SPI url cannot be empty."

        messages.add_message(
            request,
            message_level,
            message_text
        )
        return redirect('services:spi_list',
                        service_command_id=service_command_id,
                        command_id=command_id,
                        service_id=service_id)

    def get_context_data(self, **kwargs):
        context = super(SPIView, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        if not service_command_id:
            raise Http404
        success, status_code, data = self.get_spi_list(service_command_id)
        if success:
            data_spi_call_method = self.get_call_method()
            spi_types = self.get_spi_types()
            context['data'] = data
            context['data_spi_call_method'] = data_spi_call_method
            context['spi_types'] = spi_types
            context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
            context['spi_update_msg'] = self.request.session.pop('spi_update_msg', None)
            context['spi_delete_msg'] = self.request.session.pop('spi_delete_msg', None)
            context['api_version'] = api_settings.API_VERSION
            return context
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def get_spi_types(self):
        self.logger.info('========== Start getting spi url types ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.SPI_TYPES_PATH, loggers=self.logger, headers=self._get_headers())
        self.logger.info('========== finish get spi url types ==========')
        return data

    def add_spi(self, service_command_id, params):
        self.logger.info("========== Start adding SPI URL by service command ==========")
        path = api_settings.SPI_ADD_PATH.format(service_command_id)
        success, status_code, message, data = RestFulClient.post(
                url = path,
                headers=self._get_headers(),
                loggers=self.logger,
                params=params)
        self.logger.info("param is : {}".format(params))
        self.logger.info("========== Finish adding SPI URL by service command ==========")
        return success, status_code, message, data

    def get_call_method(self):
        self.logger.info('========== Start getting spi call method ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.SPI_CALL_METHOD_PATH, loggers=self.logger, headers=self._get_headers())
        self.logger.info('========== finish get spi call method ==========')
        return data

    def get_spi_list(self, service_command_id):
        self.logger.info('========== Start getting SPI url list ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.SPI_LIST_PATH.format(service_command_id), loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                            status_code=status_code)
        self.logger.info('========== finish get SPI url list ==========')
        return success, status_code, data
