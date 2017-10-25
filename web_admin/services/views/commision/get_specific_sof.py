import logging
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from web_admin import api_settings, setup_logger, RestFulClient
from django.views.generic.base import View
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class GetSpecificSOF(View, GetHeaderMixin):
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
            is_success, status_code, status_message, data = RestFulClient.post(
                                                            url=path,
                                                            headers=self._get_headers(),
                                                            loggers=self.logger,
                                                            params=params)
            msg = status_message or ''
            if status_code in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
                logger.info("{} for {} username".format(msg, request.user))
                msg.add_message(request, messages.INFO, str('Your login credentials have expired. Please login again.'))
                code = 1
                response = JsonResponse({"status": code, "msg": msg})

            if status_code == "success":
                code = 2
                response = JsonResponse({"status": code, "msg": msg, "data":data['cash_sofs']})
            else:
                code = 3
                response = JsonResponse({"status": code, "msg": msg})
        else:
            path = api_settings.BANK_SOFS_URL
            params['user_type_id'] = 2
            response = ajax_functions._post_method(request, path, "", self.logger, params)
        self.logger.info('========== Finish getting Specific SOF ==========')
        return response
