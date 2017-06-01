import copy
import logging
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions
from web_admin.api_settings import GLOBAL_CONFIGURATIONS_URL
from web_admin.api_settings import ADD_COUNTRY_CODE_URL

logger = logging.getLogger(__name__)


class CountryCode(View, RESTfulMethods):
    def get(self, request, *args, **kwargs):
        url = GLOBAL_CONFIGURATIONS_URL
        data, success = self._get_method(api_path=url,
                                         func_description="global configurations",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            context = {'country_code': data['country']}
        else:
            context = {'country_code': None}

        return render(request, 'country/country_code.html', context)

    def post(self, request, *args, **kwargs):
        logger.info('========== Start add country code ==========')
        country_code = request.POST.get('country_code')
        params = {
            'value': "" + country_code,
        }
        url = ADD_COUNTRY_CODE_URL
        data_log = copy.deepcopy(params)
        data_log['client_secret'] = ''
        result = ajax_functions._put_method(request, url, "", logger, params)
        logger.info('========== Finish add country code ==========')
        return result

