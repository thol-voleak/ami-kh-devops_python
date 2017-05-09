import logging
from multiprocessing.pool import ThreadPool
from authentications.apps import InvalidAccessToken
import requests
from django.conf import settings

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class GetChoicesMixin(object):
    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def _get_currency_choices(self):
        url = settings.GET_ALL_CURRENCY_URL
        logger.info('Get currency choice list from backend')
        logger.info('Request url: {}'.format(url))
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        response_json = response.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            value = response_json.get('data', {}).get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return result


    def _get_service_group_choices(self):
        url = settings.SERVICE_GROUP_LIST_URL
        logger.info('Get services group list from backend')
        logger.info('Request url: {}'.format(url))
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        response_json = response.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            json_data = response.json()
            return json_data.get('data'), True
        else:
            result = [], False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return result


    def _get_service_group_and_currency_choices(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        service_groups, success_service = self._get_service_group_choices()
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        return None, False
