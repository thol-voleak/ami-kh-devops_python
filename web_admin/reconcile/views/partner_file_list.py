import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PartnerFileList(TemplateView, RESTfulMethods):
    template_name = "reconcile/partner_file_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PartnerFileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        choices, success = self._get_service_group_and_currency_choices()
        return render(request, self.template_name, {'choices': choices})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search partner file list ==========')

        is_on_us = int(request.POST.get('on_off_us_id'))

        params = {}

        if is_on_us >= 0:
            params['is_on_us'] = is_on_us

        data = self._search_file_list(params)

        choices, success = self._get_service_group_and_currency_choices()
        context = {'choices': choices,
                   'file_list': data}
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def _search_file_list(self, params):
        api_path = api_settings.SEARCH_RECONCILE_PARTNER_FILE_LIST

        data, success = self._post_method(
            api_path=api_path,
            func_description="Search Partner File List",
            logger=logger,
            params=params
        )
        self.logger.info("data={}".format(data))
        return data

    def _get_currency_choices(self):
        self.logger.info('========== Start Getting Currency Choices ==========')
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(url, "currency choice", logger)

        if success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
        self.logger.info('========== Finish Getting Currency Choices ==========')
        return result

    def _get_service_group_choices(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        return self._get_method(url, "services group list", logger, True)

    def _get_service_group_and_currency_choices(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        self.logger.info('========== Start Getting Service Group Choices ==========')
        service_groups, success_service = self._get_service_group_choices()
        self.logger.info('========== Finish Getting Service Group Choices ==========')
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        return None, False