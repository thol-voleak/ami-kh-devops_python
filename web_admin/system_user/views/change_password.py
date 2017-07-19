from authentications.utils import get_correlation_id_from_username
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from django.contrib import messages
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import encrypt_text, setup_logger

logger = logging.getLogger(__name__)


class SystemUserChangePassword(TemplateView, RESTfulMethods):
    template_name = "system_user/system_user_change_password.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SystemUserChangePassword, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:

            context = super(SystemUserChangePassword, self).get_context_data(**kwargs)
            system_user_id = context['systemUserId']

            system_user_info = {
                "id": system_user_id,
                "password": None,
            }
            context = {'system_user_info': system_user_info}
            return context
        except Exception as ex:
            self.logger.info(ex)
            context = {'system_user_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start changing system user password ==========')
        system_user_id = kwargs['systemUserId']
        url = api_settings.CHANGE_PASSWORD_SYSTEM_USER_URL.format(system_user_id)
        password = request.POST.get('newpassword')
        params = {"password": encrypt_text(password)}
        data, success = self._put_method(api_path=url,
                                         func_description="password",
                                         params=params)
        self.logger.info('========== Finish changing system user password ==========')
        if success:
            messages.add_message(request, messages.SUCCESS, 'Password has been changed successfully')
            return redirect('system_user:system-user-list')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid request')
            return redirect('system_user:system-user-change-password', systemUserId=system_user_id)
