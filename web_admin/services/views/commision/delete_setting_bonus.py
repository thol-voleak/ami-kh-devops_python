import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from django.views.generic.base import View
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
logger = logging.getLogger(__name__)

class DeleteSettingBonus(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteSettingBonus, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting Bonus Distribution ==========')
        bonus_distribution_id = kwargs.get('bonus_distribution_id')
        api_path = api_settings.BONUS_SETTINGS_DELETE_PATH.format(
            bonus_distribution_id=bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        response = ajax_functions._delete_method(request, url, "", self.logger)
        self.logger.info('========== Finish deleting Bonus Distribution ==========')
        return response