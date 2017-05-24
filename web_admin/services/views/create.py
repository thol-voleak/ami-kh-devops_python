from django.views.generic.base import TemplateView
from django.conf import settings
from web_admin import api_settings
from django.shortcuts import redirect, render
from django.contrib import messages
from multiprocessing.pool import ThreadPool
import logging
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class CreateView(TemplateView, RESTfulMethods):
    template_name = "service_create.html"

    def get(self, request, *args, **kwargs):
        choices, success = self._get_service_group_and_currency_choices()
        if not success:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
            return redirect('services:services_list')
        return render(request, self.template_name, {'choices': choices})

    def post(self, request, *args, **kwargs):
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

        data, success = self._create_service(body)
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added service successfully'
            )
            return redirect('services:service_detail', ServiceId=data['service_id'])
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!',
            )
            return redirect('services:service_create')

    def _create_service(self, data):
        url = settings.SERVICE_CREATE_URL
        return self._post_method(url, "Service", logger, data)


    def _get_currency_choices(self):
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
        return result


    def _get_service_group_choices(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        return self._get_method(url, "services group list", logger, True)

    def _get_service_group_and_currency_choices(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        service_groups, success_service = self._get_service_group_choices()
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        return None, False