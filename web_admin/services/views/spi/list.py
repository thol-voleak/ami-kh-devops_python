from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
import logging
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)


class SPIView(TemplateView, RESTfulMethods):
    template_name = 'services/spi/list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start adding SPI URL by service command ==========")

        service_command_id = kwargs.get('service_command_id')
        if not service_command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url = request.POST.get('spi_url_value')
        connection_timeout = request.POST.get('connection_timeout')
        read_timeout = request.POST.get('read_timeout')

        params = {
            "spi_url_type": spi_type,
            "url": spi_url,
            "spi_url_call_method": "asynchronous",
            "expire_in_minute": 3,
            "max_retry": 2,
            "retry_delay_millisecond": 289,
        }

        if connection_timeout.isdigit() and connection_timeout != '0':
            params['connection_timeout'] = connection_timeout
        else:
            params['connection_timeout'] = 3600

        if read_timeout.isdigit() and read_timeout != '0':
            params['read_timeout'] = read_timeout
        else:
            params['read_timeout'] = 3600

        data, success = self.add_spi(service_command_id, params)
        self.logger.info("========== Finish adding SPI URL by service command ==========")

        if success:
            request.session['add_spi_url_msg'] = 'Added SPI URL successfully'
            return redirect(request.META['HTTP_REFERER'])


    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting SPI url list ==========')
        context = super(SPIView, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        if not service_command_id:
            raise Http404
        data, success = self.get_spi_list(service_command_id)
        spi_types, success2 = self.get_spi_types()

        context['data'] = data
        context['spi_types'] = spi_types
        context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
        context['spi_update_msg'] = self.request.session.pop('spi_update_msg', None)
        context['spi_delete_msg'] = self.request.session.pop('spi_delete_msg', None)
        self.logger.info('========== Finish getting SPI url list ==========')
        return context

    def get_spi_list(self, service_command_id):
        path = api_settings.SPI_LIST_PATH.format(service_command_id)
        return self._get_method(path, '', logger, True)

    def get_spi_types(self):
        path = api_settings.SPI_TYPES_PATH
        return self._get_method(path, 'SPI Types', logger, True)

    def add_spi(self, service_command_id, params):
        path = api_settings.SPI_ADD_PATH.format(service_command_id)
        return self._post_method(path, "SPI Types", logger, params)

