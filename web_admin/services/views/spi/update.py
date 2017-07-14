from services.views.spi import SpiApi
from web_admin import api_settings
from web_admin.utils import setup_logger

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class SPIUpdate(TemplateView, SpiApi):
    template_name = 'services/spi/update.html'
    get_call_method_url = 'api-gateway/payment/v1/spi-url-call-methods'

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SPIUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating SPI URL by service command ==========")

        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spiUrlId')

        if not service_command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url = request.POST.get('spi_url_value')
        spi_url_call_method = request.POST.get('spi_url_call_method')
        connection_timeout = request.POST.get('connection_timeout', '')
        read_timeout = request.POST.get('read_timeout', '')
        max_retry = request.POST.get('max_retry', '')
        retry_delay = request.POST.get('retry_delay', '')
        expire_in_minute = request.POST.get('expire_in_minute', '')

        params = {
            "service_command_id": service_command_id,
            "spi_url_type": spi_type,
            "url": spi_url,
            "spi_url_call_method": spi_url_call_method,
            "expire_in_minute": '' if expire_in_minute == "" else int(expire_in_minute),
            "max_retry": '' if max_retry == "" else int(max_retry),
            "retry_delay_millisecond": '' if retry_delay == "" else int(retry_delay),
            "read_timeout": '' if read_timeout == "" else int(read_timeout),
            "connection_timeout": '' if connection_timeout == "" else int(connection_timeout)
        }

        data, success = self.update_spi(spi_url_id, params)
        self.logger.info("========== Finish updating SPI URL by service command ==========")

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            return redirect('services:spi_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                data
            )
            return redirect('services:spi_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting SPI url list ==========')
        context = super(SPIUpdate, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        spi_url_id = kwargs.get('spiUrlId')

        data_spi_call_method, status_call_method = self.get_call_method()
        if not service_command_id:
            raise Http404

        spi_types, success = self.get_spi_types()
        data, success2 = self.get_spi_detail(spi_url_id)

        context['data'] = data
        context['spi_types'] = spi_types
        context['data_spi_call_method'] = data_spi_call_method
        context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
        self.logger.info('========== Finish getting SPI url list ==========')
        return context

    def get_spi_detail(self, spi_url_id):
        path = api_settings.SPI_DETAIL_PATH.format(spiUrlId=spi_url_id)
        return self._get_method(path, '', logger)

    def get_spi_types(self):
        path = api_settings.SPI_TYPES_PATH
        return self._get_method(path, 'SPI Types', logger, True)

    def update_spi(self, spi_url_id, params):
        path = api_settings.SPI_UPDATE_PATH.format(spiUrlId=spi_url_id)
        return self._put_method(path, 'SPI update', logger, params)
