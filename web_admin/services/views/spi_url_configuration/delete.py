from services.views.spi import SpiApi
from authentications.utils import get_correlation_id_from_username

from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

from web_admin import api_settings

logger = logging.getLogger(__name__)


class SPIUrlConfigurationDelete(TemplateView, SpiApi):
    template_name = 'services/spi_url_configuration/delete.html'
    get_config_type_url = 'api-gateway/payment/'+api_settings.API_VERSION+'/spi-url-configuration-types'
    spi_url_configuration = 'api-gateway/payment/'+api_settings.API_VERSION+'/spi-url-configurations/{spiUrlConfigurationId}'

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SPIUrlConfigurationDelete, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting SPI url detail ==========')
        context = super(SPIUrlConfigurationDelete, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')
        spi_url_config_id = kwargs.get('spi_url_config_id')

        configuration_detail, success = self._get_method(
            self.spi_url_configuration.format(spiUrlConfigurationId=spi_url_config_id),
            "Get spi url configuration", logger)
        self.logger.info("SPI Url configuration details is [{}]".format(configuration_detail))

        data, success = self._get_method(self.get_config_type_url, "", logger)
        self.logger.info("SPI url configuration types {}".format(data))
        self.logger.info('========== Finish getting SPI url detail ==========')
        context['configuration_detail'] = configuration_detail
        context['configuration_type_list'] = data
        context['service_command_id'] = service_command_id
        context['service_id'] = service_id
        context['command_id'] = command_id
        context['spi_url_id'] = spi_url_id
        context['spi_url_config_id'] = spi_url_config_id
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start deleting SPI configuration url ==========")
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')
        spi_url_config_id = kwargs.get('spi_url_config_id')

        path = self.spi_url_configuration.format(spiUrlConfigurationId=spi_url_config_id)
        data, status = self._delete_method(path, "Delete SPI Configuration Url", logger)

        self.logger.info("spi url configuration types {}".format(data))
        self.logger.info("========== Finish deleting SPI configuration url ==========")
        if status:
            type_msg = messages.SUCCESS
            text_msg = 'Deleted data successfully'
        else:
            type_msg = messages.ERROR
            text_msg = data

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
