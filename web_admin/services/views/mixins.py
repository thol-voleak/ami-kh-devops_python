import logging
from django.views.generic.base import View
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)

class GetCommandNameAndServiceNameMixin(View, GetHeaderMixin):
    logger = logger
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(GetCommandNameAndServiceNameMixin, self).dispatch(request, *args, **kwargs)

    def _get_command_name_by_id(self, command_id):
        url = api_settings.COMMAND_LIST_URL
        is_success, status_code, data = RestFulClient.get(url=url,
                                                         headers=self._get_headers(),
                                                         loggers= self.logger)
        if is_success:
            command_name = [d['command_name']
                            for d in data
                            if str(d['command_id']) == str(command_id)]
            if command_name:
                return command_name[0]
        else:
            return command_id

    def _get_service_name_by_id(self, service_id):
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        is_success, status_code, data = RestFulClient.get(url=url,
                                                         headers=self._get_headers(),
                                                         loggers= self.logger)
        if is_success:
            return data.get('service_name', service_id)
        else: 
            return None


    def _get_specific_ids(self):
        count = 0
        self.logger.info('========== Start Getting Specific IDs ==========')
        params = {
            "paging":False,
            "page_index":0            
        }
        is_success, status_code, status_message, data = RestFulClient.post(
                                                        url=api_settings.AGENT_LIST_PATH,
                                                        headers=self._get_headers(),
                                                        loggers= self.logger,
                                                        params=params)
        if is_success:
            count = len(data)
            self.logger.info("Response_content_count:{}".format(len(data)))
            data = [i.get('id') for i in data['agents'] if not i.get('is_deleted')]
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        self.logger.info('========== Finish Get Specific Ids ==========')
        
        return data
