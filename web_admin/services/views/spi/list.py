from web_admin import api_settings
from web_admin.utils import setup_logger
from services.views.spi import SpiApi

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class SPIView(TemplateView, SpiApi):
    template_name = 'services/spi/list.html'
    get_call_method_url = 'api-gateway/payment/v1/spi-url-call-methods'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start adding SPI URL by service command ==========")

        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        if not service_command_id or not service_id or not command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url = request.POST.get('spi_url_value')
        spi_url_call_method = request.POST.get('spi_url_call_method')
        connection_timeout = request.POST.get('connection_timeout', 0)
        read_timeout = request.POST.get('read_timeout', 0)
        max_retry = request.POST.get('max_retry', 0)
        retry_delay = request.POST.get('retry_delay', 0)
        expire_in_minute = request.POST.get('expire_in_minute', 0)

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
            data, success = self.add_spi(service_command_id, params)
            self.logger.info("========== Finish adding SPI URL by service command ==========")

            if success:
                message_level = messages.SUCCESS
                message_text = 'Added SPI URL successfully'
            else:
                message_level = messages.ERROR
                message_text = data
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
        self.logger.info('========== Start getting SPI url list ==========')
        context = super(SPIView, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        if not service_command_id:
            raise Http404
        data, success = self.get_spi_list(service_command_id)
        data_spi_call_method, status_call_method = self.get_call_method()
        spi_types, success2 = self.get_spi_types()

        context['data'] = data
        context['data_spi_call_method'] = data_spi_call_method
        context['spi_types'] = spi_types
        context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
        context['spi_update_msg'] = self.request.session.pop('spi_update_msg', None)
        context['spi_delete_msg'] = self.request.session.pop('spi_delete_msg', None)
        self.logger.info('========== Finish getting SPI url list ==========')
        return context

    def get_spi_types(self):
        path = api_settings.SPI_TYPES_PATH
        return self._get_method(path, 'SPI Types', logger, True)

    def add_spi(self, service_command_id, params):
        path = api_settings.SPI_ADD_PATH.format(service_command_id)
        return self._post_method(path, "SPI Types", logger, params)
