from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from services.views.spi import SpiApi

from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class SPIUrlConfigurationView(TemplateView, SpiApi):
    template_name = 'services/spi_url_configuration/list.html'
    get_config_type_url = 'api-gateway/payment/v1/spi-url-configuration-types'
    spi_url_configuration = 'api-gateway/payment/v1/spi-urls/{spiUrlId}/spi-url-configurations'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SPIUrlConfigurationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting SPI configuration url list ==========')
        context = super(SPIUrlConfigurationView, self).get_context_data(**kwargs)

        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spiUrlId')

        configuration_data, configuration_status = self._get_method(
            self.spi_url_configuration.format(spiUrlId=spi_url_id),
            "Get all spi url configuration",
            logger)

        data, success = self._get_method(self.get_config_type_url, "Get all spi url configuration types", logger, True)
        self.logger.info("spi url configuration types {}".format(data))

        context['configuration_data'] = configuration_data
        context['configuration_type_list'] = data
        context['service_command_id'] = service_command_id
        context['service_id'] = service_id
        context['command_id'] = command_id
        context['spiUrlId'] = spi_url_id
        self.logger.info('========== Finish getting SPI configuration url list ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start adding SPI configuration url ==========")
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spiUrlId')

        if not service_command_id or not service_id or not command_id:
            raise Http404

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
        self.logger.info("request params [{}]".format(params))
        path = self.spi_url_configuration.format(spiUrlId=spi_url_id)
        data, status = self._post_method(path, "Adding SPI configuration url", logger, params)

        self.logger.info("spi url configuration types {}".format(data))
        self.logger.info("========== Finish adding SPI configuration url ==========")
        if status:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added SPI configuration successfully'
            )
            return redirect('services:spi_configuration_list',
                            service_command_id=service_command_id,
                            service_id=service_id,
                            command_id=command_id,
                            spiUrlId=spi_url_id)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                data
            )
            configuration_data, configuration_status = self._get_method(
                self.spi_url_configuration.format(spiUrlId=spi_url_id),
                "Get all spi url configuration",
                logger)

            data, success = self._get_method(self.get_config_type_url, "Get all spi url configuration types", logger)
            self.logger.info("spi url configuration types {}".format(data))
            context = {}
            context['configuration_data'] = configuration_data
            context['configuration_type_list'] = data
            context['service_command_id'] = service_command_id
            context['service_id'] = service_id
            context['command_id'] = command_id
            context['spiUrlId'] = spi_url_id
            context['params'] = params
            return render(request, self.template_name, context)

