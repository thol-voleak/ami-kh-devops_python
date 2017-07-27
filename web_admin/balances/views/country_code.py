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


class CountryCode(TemplateView, RESTfulMethods):
    template_name = "country/country_code.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CountryCode, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not check_permissions_by_user(self.request.user, "SYS_VIEW_COUNTRYCODE"):
            return redirect('web:permission_denied')

        url = GLOBAL_CONFIGURATIONS_URL
        data, success = self._get_method(api_path=url,
                                         func_description="global configurations",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            context = {'country_code': data['country']}
        else:
            context = {'country_code': None}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not check_permissions_by_user(self.request.user, "SYS_CREATE_COUNTRYCODE"):
            return redirect('web:permission_denied')

        self.logger.info('========== Start add country code ==========')
        country_code = request.POST.get('country_code')
        params = {
            'value': "" + country_code,
        }
        url = ADD_COUNTRY_CODE_URL
        data_log = copy.deepcopy(params)
        data_log['client_secret'] = ''
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish add country code ==========')
        return result
