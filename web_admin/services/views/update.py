from authentications.utils import get_auth_header
from web_admin.api_settings import SERVICE_GROUP_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from web_admin import api_settings
from django.shortcuts import redirect, render
from multiprocessing import Process, Manager
from django.contrib import messages
from web_admin import ajax_functions
from web_admin.utils import setup_logger
import logging
import json

logger = logging.getLogger(__name__)


class UpdateView(TemplateView, RESTfulMethods):
    template_name = "services/service_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        service_id = context['service_id']

        manager = Manager()
        return_dict = manager.dict()

        currencies, status1 = self._get_currency_choices()

        p2 = Process(target=self._get_service_group_choices, args=(2, return_dict))
        p2.start()
        p3 = Process(target=self._get_service_detail, args=(3, return_dict, service_id))
        p3.start()
        p2.join()
        p3.join()

        service_groups, status2 = return_dict[2]
        service_detail, status3 = return_dict[3]


        if p2.is_alive():
            p2.terminate()

        if p3.is_alive():
            p3.terminate()

        if status1 and status2 and status3:
            context = {
                'currencies': currencies,
                'service_groups': service_groups,
                'service_detail': service_detail,
                'service_id': service_id
            }
            return render(request, self.template_name, context)
        else:
            return None

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating Service ==========')
        service_id = kwargs['service_id']
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_name')
        currency = request.POST.get('currency')
        description = request.POST.get('description')

        data = {
            'service_group_id': service_group_id,
            'service_name': service_name,
            'currency': currency,
            'description': description,
            'status': '1'
        }

        url = api_settings.SERVICE_UPDATE_URL.format(service_id)
        result = ajax_functions._put_method(request, url, "Service", logger, data)
        self.logger.info('========== Finish updating Service ==========')

        response = json.loads(result.content)

        if response["status"] == 2:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
        return result


    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _get_currency_choices(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(url, "currency choices", logger)
        if success:
            value = data.get('value', '')
            currency_list = self._get_currency_list(value)
            return currency_list, True
        else:
            return [], True

    def _get_currency_list(self, value):
        result = []
        list = value.split(',')
        for item in list:
            currency = item.split('|')
            result.append(currency)

        return result

    def _get_service_group_choices(self, procnum, dict):
        dict[procnum] = self._get_method(SERVICE_GROUP_LIST_URL, "service group choices", logger, True)

    def _get_service_detail(self, procnum, dict, service_id):
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        dict[procnum] = self._get_method(url, "service detail", logger, True)
