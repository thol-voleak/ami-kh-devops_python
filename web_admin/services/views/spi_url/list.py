from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from django.http import Http404
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class SPIView(TemplateView, RESTfulMethods):
    template_name = 'services/spi_url/list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting SPI url list ==========')
        context = super(SPIView, self).get_context_data(**kwargs)
        service_command_id = kwargs.get('service_command_id')
        if not service_command_id:
            raise Http404
        data, success = self.get_spi_list(service_command_id)

        context['data'] = data
        logger.info('========== Finish getting SPI url list ==========')
        return context

    def get_spi_list(self, service_command_id):
        path = api_settings.SPI_LIST_PATH.format(service_command_id)
        return self._get_method(path, '', logger, True)
