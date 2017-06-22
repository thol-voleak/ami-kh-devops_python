from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings

import logging

logger = logging.getLogger(__name__)


class SpiApi(RESTfulMethods):
    def get_spi_list(self, service_command_id):
        path = api_settings.SPI_LIST_PATH.format(service_command_id)
        return self._get_method(path, '', logger, True)

    def get_call_method(self):
        path = self.get_call_method_url
        return self._get_method(path, '', logger, True)