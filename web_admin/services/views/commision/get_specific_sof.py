import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from django.views.generic.base import View
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
logger = logging.getLogger(__name__)


class GetSpecificSOF(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(GetSpecificSOF, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting Specific SOF ==========')
        user_id = kwargs.get('user_id')
        sof_type = kwargs.get('sof_type')
        params = {
            'user_id': user_id,
        }
        if sof_type == '2':
            path = api_settings.CASH_SOFS_URL
            params['user_type'] = int(sof_type)
        else:
            path = api_settings.BANK_SOFS_URL
            params['user_type_id'] = 2
        url = settings.DOMAIN_NAMES + path
        response = ajax_functions._post_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish getting Specific SOF ==========')
        return response
