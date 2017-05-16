import logging
import time
import requests
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)


class DeleteSettingBonus(View, GetHeaderMixin):
    def delete(self, request, *args, **kwargs):
        bonus_distribution_id = kwargs.get('bonus_distribution_id')

        logger.info('========== Start delete Setting Bonus on commission and payment method ==========')
        success = self._delete_setting_bonus(bonus_distribution_id)
        logger.info('========== Finish delete Setting Bonus on commission and payment method ==========')

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_setting_bonus(self, bonus_distribution_id):
        api_path = settings.BONUS_SETTINGS_DELETE_PATH.format(
            bonus_distribution_id=bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.delete(url, headers=self._get_headers(),
                                   verify=settings.CERT)
        done = time.time()
        logger.info('Reponse_time: {}'.format(done - start_date))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.content))
        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
        

        if response.status_code == 200:
            return True
        return False
