import logging
from django.conf import settings
from web_admin import api_settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class DeleteSettingBonus(View, RESTfulMethods):
    def delete(self, request, *args, **kwargs):
        bonus_distribution_id = kwargs.get('bonus_distribution_id')
        data, success = self._delete_setting_bonus(bonus_distribution_id)
        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_setting_bonus(self, bonus_distribution_id):
        api_path = api_settings.BONUS_SETTINGS_DELETE_PATH.format(
            bonus_distribution_id=bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        return self._delete_method(url, "Setting Bonus on commission and payment", logger)