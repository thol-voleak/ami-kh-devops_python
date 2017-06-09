from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


class SPIUpdate(TemplateView, RESTfulMethods):
    template_name = 'services/spi/update.html'

    def post(self, request, *args, **kwargs):
        logger.info("========== Start updating SPI URL by service command ==========")

        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spiUrlId = kwargs.get('spiUrlId')

        if not service_command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url = request.POST.get('spi_url_value')
        connection_timeout = request.POST.get('connection_timeout')
        read_timeout = request.POST.get('read_timeout')

        params = {
           "service_command_id":service_command_id,
           "spi_url_type":spi_type,
           "url":spi_url,
           "spi_url_call_method":"asynchronous",
           "expire_in_minute":7,
           "max_retry":8,
           "retry_delay_millisecond":785
        }

        if connection_timeout.isdigit() and connection_timeout != '0':
            params['connection_timeout'] = connection_timeout
        else:
            params['connection_timeout'] = 3600

        if read_timeout.isdigit() and read_timeout != '0':
            params['read_timeout'] = read_timeout
        else:
            params['read_timeout'] = 3600

        data, success = self.update_spi(spiUrlId, params)
        logger.info("========== Finish updating SPI URL by service command ==========")

        if success:
            request.session['spi_update_msg'] = 'Updated data successfully'
            return redirect('services:spi_list', service_id=(service_id), command_id=(command_id), service_command_id=(service_command_id) )

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting SPI url list ==========')
        context = super(SPIUpdate, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        spiUrlId = kwargs.get('spiUrlId')
        if not service_command_id:
            raise Http404

        spi_types, success = self.get_spi_types()
        data, success2 = self.get_spi_detail(spiUrlId)

        context['data'] = data
        context['spi_types'] = spi_types
        context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
        logger.info('========== Finish getting SPI url list ==========')
        return context

    def get_spi_detail(self, spiUrlId):
        path = api_settings.SPI_DETAIL_PATH.format(spiUrlId=spiUrlId)
        return self._get_method(path, '', logger)

    def get_spi_types(self):
        path = api_settings.SPI_TYPES_PATH
        return self._get_method(path, 'SPI Types', logger, True)

    def update_spi(self, spiUrlId, params):
        path = api_settings.SPI_UPDATE_PATH.format(spiUrlId=spiUrlId)
        return self._put_method(path, '', logger, params)
