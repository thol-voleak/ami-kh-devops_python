from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from multiprocessing.pool import ThreadPool
from django.contrib import messages

import requests
import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView):
    template_name = "service_create.html"

    def get(self, request, *args, **kwargs):
        choices, success = self._get_dropdown_choices()
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

        data = {
            'service_group_id': service_group_id,
            'service_name': service_name,
            'currency': currency,
            'description': description,
        }

        logger.info('========== Start create new Service ==========')
        data, success = self._create_service(data)
        logger.info('========== Finished create new Service ==========')
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added service successfully'
            )
            return redirect('services:services_list')
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!',
            )
            return redirect('services:service_create')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def _create_service(self, data):
        logger.info("Creating service by user {}".format(self.request.user.username))

        url = settings.SERVICE_CREATE_URL

        logger.info('Request url: {}'.format(url))
        logger.info('Request body: {}'.format(data))
        response = requests.post(url, headers=self._get_headers(),
                                 json=data, verify=False)

        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))


        json_data = response.json()
        if response.status_code == 200:
            return json_data.get('data'), True
        else:
            logger.info("Received response with status {}".format(response.status_code))
            logger.info("Response content is {}".format(response.content))
            return None, False

    def _get_currency_choices(self):
        url = settings.GET_ALL_CURRENCY_URL
        logger.info('Get currency choice list from backend')
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            json_data = response.json()
            value = json_data.get('data', {}).get('value', '')
            currency_list = map(lambda x: x.split('|'), value.split(','))
            return currency_list, True
        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))
        return None, False

    def _get_service_group_choices(self):
        url = settings.SERVICE_GROUP_LIST_URL
        logger.info('Get services group list from backend')
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data'), True
        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))
        return None, False

    def _get_dropdown_choices(self):
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
