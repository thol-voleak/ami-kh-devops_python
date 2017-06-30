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


class SofFileList(TemplateView, RESTfulMethods):
    template_name = "reconcile/sof_file_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SofFileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        currencies, success = self._get_currency_choices()
        return render(request, self.template_name, {'currencies': currencies})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search sof file list ==========')

        is_on_us = int(request.POST.get('on_off_us_id'))

        params = {}

        if is_on_us >= 0:
            params['is_on_us'] = is_on_us

        data = self._search_file_list(params)

        currencies, success = self._get_currency_choices()
        context = {'currencies': currencies,
                   'file_list': data}
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def _search_file_list(self, params):
        api_path = api_settings.SEARCH_RECONCILE_SOF_FILE_LIST

        data, success = self._post_method(
            api_path=api_path,
            func_description="Search sof File List",
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