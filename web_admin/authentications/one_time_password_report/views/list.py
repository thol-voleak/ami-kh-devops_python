from web_admin import setup_logger, RestFulClient, api_settings
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class OTPList(TemplateView):

    template_name = "one_time_password_report/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(OTPList, self).dispatch(request, *args, **kwargs)


