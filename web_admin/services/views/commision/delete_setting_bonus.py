import logging
from django.conf import settings
from web_admin import api_settings
from django.views.generic.base import View
from web_admin import ajax_functions
logger = logging.getLogger(__name__)

class DeleteSettingBonus(View):
    def delete(self, request, *args, **kwargs):
        logger.info('========== Start deleting Bonus Distribution ==========')
        bonus_distribution_id = kwargs.get('bonus_distribution_id')
        api_path = api_settings.BONUS_SETTINGS_DELETE_PATH.format(
            bonus_distribution_id=bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        response = ajax_functions._delete_method(request, url, "", logger)
        logger.info('========== Finish deleting Bonus Distribution ==========')
        return response