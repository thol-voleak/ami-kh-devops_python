from authentications.utils import get_correlation_id_from_username
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging
from django.conf import settings
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.utils import encrypt_text, setup_logger
from authentications.apps import InvalidAccessToken
from django.contrib import messages

logger = logging.getLogger(__name__)


class SelfChangePassword(TemplateView, GetHeaderMixin):
    template_name = "system_user/self_change_password.html"
    logger = logger
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SelfChangePassword, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== User go to Change Password page ==========')
        return render(request, self.template_name, context={'update_passwd_success': False})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== User start updating password ==========')
        url = api_settings.CHANGE_PASSWD
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        body = {
            'old_password': encrypt_text(old_password),
            'new_password': encrypt_text(new_password),
        }

        success, status_code, message, data = RestFulClient.put(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            timeout=settings.GLOBAL_TIMEOUT,
            params=body)

        self.logger.info('========== User finish updating password ==========')
        if success:
            return render(request, self.template_name, context={'update_passwd_success': True})
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(message))
                raise InvalidAccessToken(message)

            body = {
                'old_password': old_password,
                'new_password': new_password,
                "confirm_new_password": request.POST.get('confirm_new_password')
            }

            if status_code.lower() in ["invalid_request"]:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Password change failed as it not met password criteria or old password didn’t match. Please review and try again."
                )

            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Password change failed. Please try again or contact support."
                )

            return render(request, self.template_name, body)


