from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging
from django.contrib import messages
from web_admin.restful_client import RestFulClient
from web_admin.utils import encrypt_text, setup_logger

logger = logging.getLogger(__name__)


class ChangePasswd(TemplateView):
    template_name = "system_user/change_passwd.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ChangePasswd, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
            return redirect('system_user:change_passwd')
