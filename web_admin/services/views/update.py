from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from multiprocessing import Process, Manager
from django.contrib import messages

import requests
import logging

logger = logging.getLogger(__name__)


class UpdateView(TemplateView):
    template_name = "services/service_update.html"

    def get(self, request, *args, **kwargs):
        logger.info('========== Start getting currencies, service groups, service detail ==========')

        context = super(UpdateView, self).get_context_data(**kwargs)
        service_id = context['service_id']
        header = self._get_headers()

        manager = Manager()
        return_dict = manager.dict()

        p1 = Process(target=self._get_currency_choices, args=(1, return_dict))
        p1.start()
        p2 = Process(target=self._get_service_group_choices, args=(2, return_dict))
        p2.start()
        p3 = Process(target=self._get_service_detail, args=(3, return_dict, service_id))
        p3.start()
        p1.join()
        p2.join()
        p3.join()

        currencies, status1 = return_dict[1]
        service_groups, status2 = return_dict[2]
        service_detail, status3 = return_dict[3]

        if p1.is_alive():
            p1.terminate()

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
            logger.info('========== Finish getting currencies, service groups, service detail ==========')
            return render(request, self.template_name, context)
        else:
            logger.info('========== Finish getting currencies, service groups, service detail ==========')
            return None

    def post(self, request, *args, **kwargs):
        logger.info('========== Start updating service ==========')
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

        data, success = self._update_service(service_id, data)
        logger.info('========== Finish updating service ==========')
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            return redirect('services:service_detail', ServiceId=(service_id))
        else:
            return None

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _update_service(self, service_id, data):
        logger.info("Updating service by user {}".format(self.request.user.username))

        url = settings.SERVICE_UPDATE_URL.format(service_id)

        logger.info('========== Start update new Service ==========')
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))
        logger.info('Username {} sends request body: {}'.format(self.request.user.username, data))
        response = requests.put(url, headers=self._get_headers(),
                                json=data, verify=settings.CERT)
        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('========== Finished updating Service ==========')

        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data'), True
        else:
            return None, False

    def _get_currency_choices(self, procnum, dict):
        logger.info('Start getting currency choice list from backend')
        url = settings.GET_ALL_CURRENCY_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting currency choice list from backend')

        if response.status_code == 200:
            json_data = response.json()
            value = json_data.get('data', {}).get('value', '')
            currency_list = self._get_currency_list(value)
            dict[procnum] = currency_list, True
        else:
            dict[procnum] = None, False

    def _get_currency_list(self, value):
        result = []
        list = value.split(',')
        for item in list:
            currency = item.split('|')
            result.append(currency)

        return result


    def _get_service_group_choices(self, procnum, dict):
        logger.info('Start getting service groups from backend')

        url = settings.SERVICE_GROUP_LIST_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        logger.info('Get services group list from backend')
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        # logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting service groups from backend')

        if response.status_code == 200:
            json_data = response.json()
            dict[procnum] = json_data.get('data'), True
        else:
            dict[procnum] = None, False

    def _get_service_detail(self, procnum, dict, service_id):
        logger.info('Start getting service detail from backend')

        url = settings.SERVICE_DETAIL_URL.format(service_id)
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        # logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting service detail from backend')

        if response.status_code == 200:
            json_data = response.json()
            dict[procnum] = json_data.get('data'), True
        else:
            dict[procnum] = None, False
