from services.views.spi import SpiApi
from web_admin.utils import setup_logger

from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render

import logging

logger = logging.getLogger(__name__)


class SPIUrlConfigurationUpdate(TemplateView, SpiApi):
    template_name = 'services/spi_url_configuration/update.html'
    get_config_type_url = 'api-gateway/payment/v1/spi-url-configuration-types'
    spi_url_configuration = 'api-gateway/payment/v1/spi-url-configurations/{spiUrlConfigurationId}'

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SPIUrlConfigurationUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting SPI url list ==========')
        context = super(SPIUrlConfigurationUpdate, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')
        spi_url_config_id = kwargs.get('spi_url_config_id')

        configuration_detail, success = self._get_method(
            self.spi_url_configuration.format(spiUrlConfigurationId=spi_url_config_id),
            "Get spi url configuration", logger)
        self.logger.info("SPI Url configuration details is [{}]".format(configuration_detail))

        data, success = self._get_method(self.get_config_type_url, "Get all spi url configuration types", logger)
        self.logger.info("SPI url configuration types {}".format(data))

        context['configuration_detail'] = configuration_detail
        context['configuration_type_list'] = data
        context['service_command_id'] = service_command_id
        context['service_id'] = service_id
        context['command_id'] = command_id
        context['spi_url_id'] = spi_url_id
        context['spi_url_config_id'] = spi_url_config_id
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating SPI configuration url ==========")
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')
        spi_url_config_id = kwargs.get('spi_url_config_id')

        spi_url_configuration_type = request.POST.get('spi_url_configuration_type')
        url = request.POST.get('spi_url_configuration_value', '')
        connection_timeout = request.POST.get('connection_timeout', '')
        read_timeout = request.POST.get('read_timeout', '')
        max_retry = request.POST.get('max_retry', '')
        retry_delay_millisecond = request.POST.get('retry_delay_millisecond', '')
        expire_in_minute = request.POST.get('expire_in_minute', '')

        params = {
            'spi_url_configuration_type': spi_url_configuration_type,
            'url': url,
            'connection_timeout': int(connection_timeout) if connection_timeout else '',
            'read_timeout': int(read_timeout) if read_timeout else '',
            'max_retry': int(max_retry) if max_retry else '',
            'expire_in_minute': int(expire_in_minute),
            'retry_delay_millisecond': int(retry_delay_millisecond) if retry_delay_millisecond else ''
        }

        path = self.spi_url_configuration.format(spiUrlConfigurationId=spi_url_config_id)
        data, status = self._put_method(path, "Updating SPI configuration url", logger, params)

        self.logger.info("spi url configuration types {}".format(data))
        self.logger.info("========== Finish updating SPI configuration url ==========")
        if status:
            type_msg = messages.SUCCESS
            text_msg = 'Updated data successfully'
            messages.add_message(
                request,
                type_msg,
                text_msg
            )
            return redirect('services:spi_configuration_list',
                            service_command_id=service_command_id,
                            service_id=service_id,
                            command_id=command_id,
                            spiUrlId=spi_url_id)
        else:
            type_msg = messages.ERROR
            text_msg = data
            messages.add_message(
                request,
                type_msg,
                text_msg
            )

            context = super(SPIUrlConfigurationUpdate, self).get_context_data(**kwargs)

            context['service_command_id'] =  kwargs.get('service_command_id')
            context['service_id'] = kwargs.get('service_id')
            context['command_id'] = kwargs.get('command_id')
            context['spi_url_id'] = kwargs.get('spi_url_id')
            context['spi_url_config_id'] = spi_url_config_id = kwargs.get('spi_url_config_id')

            context['configuration_type_list'], none = self._get_method(self.get_config_type_url, "Get all spi url configuration types", logger)

            context['configuration_detail'] = {
                "spi_url_configuration_id":spi_url_config_id,
                "spi_url_configuration_type" : request.POST.get('spi_url_configuration_type'),
                "url" : request.POST.get('spi_url_configuration_value'),
                "connection_timeout" : request.POST.get('connection_timeout', ''),
                "read_timeout" : request.POST.get('read_timeout', ''),
                "max_retry" : request.POST.get('max_retry', ''),
                "retry_delay_millisecond" : request.POST.get('retry_delay_millisecond', ''),
                "expire_in_minute" : request.POST.get('expire_in_minute', ''),
                "created_timestamp" : request.POST.get('created_timestamp', ''),
                "last_updated_timestamp": request.POST.get('last_updated_timestamp', ''),
            }

            return render(request, self.template_name, context)
