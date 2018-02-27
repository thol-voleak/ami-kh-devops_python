from braces.views import GroupRequiredMixin
from django.views.generic import TemplateView

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions, setup_logger
from web_admin.api_settings import ADD_COUNTRY_CODE_URL, GLOBAL_CONFIGURATIONS_URL

from django.shortcuts import render, redirect

import copy
import logging

logger = logging.getLogger(__name__)


class BalanceSummary(TemplateView, RESTfulMethods):
    template_name = "balance_summary.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceSummary, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not check_permissions_by_user(self.request.user, "CAN_VIEW_BALANCE_SUMMARY"):
            return redirect('web:permission_denied')

        return render(request, self.template_name, )
