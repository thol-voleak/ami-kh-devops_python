from authentications.apps import InvalidAccessToken
from web_admin import api_settings
import logging
from web_admin.restful_client import RestFulClient

logger = logging.getLogger(__name__)


def _get_services_list(self):
    self.logger.info('========== Start Getting services list ==========')
    url = api_settings.SERVICE_LIST_URL
    is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(),
                                                      loggers=self.logger)
    if is_success:
        self.logger.info("Response_content_count:{}".format(len(data)))

    elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                status_code == 'invalid_access_token'):
        self.logger.info("{}".format(data))
        raise InvalidAccessToken(data)
    self.logger.info('========== Finish Get services list ==========')

    return data