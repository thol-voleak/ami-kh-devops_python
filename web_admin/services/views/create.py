from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from multiprocessing.pool import ThreadPool
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions
import logging
import json
from web_admin.utils import setup_logger


logger = logging.getLogger(__name__)


class CreateView(TemplateView, RESTfulMethods):
    template_name = "services/service_create.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        choices, success = self._get_service_group_and_currency_choices()
        self.dropdown_data = choices
        if not success:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
            return redirect('services:services_list')
        return render(request, self.template_name, {'choices': choices})

    def post(self, request, *args, **kwargs):
<<<<<<< HEAD
        self.logger.info('========== Start creating Service ==========')
=======
        logger.info('========== Start creating service ==========')
>>>>>>> 3e578adc1c5b5a0489b56ab639de304d2abb0b18
        context = super(CreateView, self).get_context_data(**kwargs)
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_name')
        currency = request.POST.get('currency')
        description = request.POST.get('description')

        body = {
            'service_group_id': service_group_id,
            'service_name': service_name,
            'currency': currency,
            'description': description,
        }

        url = api_settings.SERVICE_CREATE_URL
<<<<<<< HEAD
        result = ajax_functions._post_method(request, url, "", logger, body)
        self.logger.info('========== Finish creating Service ==========')

        response = json.loads(result.content)
=======
        data, success = self._post_method(api_path=url,
                                          func_description="creating service",
                                          logger=logger, params=body)
>>>>>>> 3e578adc1c5b5a0489b56ab639de304d2abb0b18

        if success:
            logger.info('========== Finish creating Service ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added service successfully'
            )
            return redirect('services:service_detail', ServiceId=data.get('service_id', ''))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )
            choices, success = self._get_service_group_and_currency_choices()
            context = {'choices': choices, 'body': body}
            return render(request, self.template_name, context)

    def _create_service(self, data):
        url = api_settings.SERVICE_CREATE_URL
        return self._post_method(url, "Service", logger, data)

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
        logger.info('========== Start Getting Service Group Choices ==========')
        service_groups, success_service = self._get_service_group_choices()
        logger.info('========== Finish Getting Service Group Choices ==========')
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        return None, False
