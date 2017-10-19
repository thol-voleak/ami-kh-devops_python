import logging
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class GetCommandNameAndServiceNameMixin(RESTfulMethods):
    def _get_command_name_by_id(self, command_id):
        url = api_settings.COMMAND_LIST_URL
        data, success = self._get_method(url, "command name by id", logger, True)
        if data != []:
            command_name = [d['command_name']
                            for d in data
                            if str(d['command_id']) == str(command_id)]
            if command_name:
                return command_name[0]
        else:
            return command_id

    def _get_service_name_by_id(self, service_id):
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        data, success = self._get_method(url, "service name by id", logger)
        return data.get('service_name', service_id)

    def _get_specific_ids(self):
        data, success = self._post_method(api_settings.AGENT_LIST_PATH, 'Specific IDs', logger)
        if success:
            return [i.get('id') for i in data['agents'] if not i.get('is_deleted')]
        return data
