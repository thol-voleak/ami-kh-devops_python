from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from web_admin.mixins import GetChoicesMixin

import requests
import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView, GetChoicesMixin):
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
