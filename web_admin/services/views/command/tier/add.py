from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from multiprocessing import Process, Manager

import time
import requests
import logging

logger = logging.getLogger(__name__)


class AddView(TemplateView):
    template_name = "tier/add_tier.html"

    def get(self, request, *args, **kwargs):
        logger.info('========== Start getting tier data ==========')

        context = super(AddView, self).get_context_data(**kwargs)
        service_id = context['service_id']
        command_id = context['command_id']
        tier_conditions, status1 = self._get_tier_condition()
        amount_types, status2 = self._get_amount_types()
        service_detail, status3 = self._get_service_detail(service_id)
        command_name, status4 = self._get_command_name(command_id)
        fee_types, status5 = self._get_fee_types()
        bonus_types, status6 = self._get_bonus_types()

        if status1 and status2 and status3 and status4 and status5 and status6:
            context.update({
                'conditions': tier_conditions,
                'fee_types': fee_types,
                'bonus_types': bonus_types,
                'amount_types': amount_types,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
            })
            logger.info('========== Finish getting tier data ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        logger.info('========== Start adding tier for service command ==========')
        command_id = kwargs['command_id']
        service_id = kwargs['service_id']
        service_command_id = kwargs['service_command_id']

        data = {
            "fee_tier_condition": request.POST.get('condition'),
            "condition_amount": request.POST.get('condition_amount'),
            "fee_type": request.POST.get('fee_type'),
            "fee_amount": request.POST.get('fee_amount'),
            "bonus_type": request.POST.get('bonus_type'),
            "bonus_amount": request.POST.get('bonus_amount'),
        }

        if(request.POST.get('bonus_type') != 'Flat value'):
            data['amount_type'] = request.POST.get('amount_type')

        success = self._add_tier(service_command_id, data)
        logger.info('========== Finish adding tier for service command ==========')
        if success:
            request.session['add_tier_msg'] = 'Added data successfully'
        return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id,
                        service_command_id=service_command_id)


    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _add_tier(self, service_command_id, data):
        logger.info("Adding tier for service command by user {}".format(self.request.user.username))

        url = settings.ADD_TIER_URL.format(service_command_id=service_command_id)

        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))
        logger.info('Username {} sends request body: {}'.format(self.request.user.username, data))
        response = requests.post(url, headers=self._get_headers(),
                                 json=data, verify=settings.CERT)
        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))

        if response.status_code == 200:
            response_json = response.json()
            status = response_json['status']
            if status['code'] == "success":
                return True
        return False

    def _get_tier_condition(self):
        logger.info('Start getting fee tier condition from backend')
        url = settings.FEE_TIER_CONDITION_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting fee tier condition from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                conditions = json_data.get('data', {})
                return conditions, True
            else:
                return None, False
        else:
            return None, False

    def _get_amount_types(self):
        logger.info('Start getting amount types from backend')

        url = settings.AMOUNT_TYPES_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        logger.info('Get amount types from backend')
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting amount types from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                return json_data.get('data', {}), True
            else:
                return None, False
        else:
            return None, False

    def _get_service_detail(self, service_id):
        logger.info('Start getting service detail {} from backend'.format(service_id))

        url = settings.SERVICE_DETAIL_URL.format(service_id)
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        headers = get_auth_header(self.request.user)

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting service detail {} from backend'.format(service_id))

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                return json_data.get('data', {}), True
            else:
                return None, False
        else:
            return None, False

    def _get_command_name(self, command_id):
        logger.info('Start getting commands list from backend')

        url = settings.COMMAND_LIST_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        headers = get_auth_header(self.request.user)

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting commands list from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                command_name = None
                commands_list = json_data.get('data', {})
                my_id = int(command_id)
                for x in commands_list:
                    if x['command_id'] == my_id:
                        command_name = x['command_name']
                        return command_name, True

                return 'Unknown', True
            else:
                return None, False
        else:
            return None, False

    def _get_fee_types(self):
        logger.info('Start getting fee types from backend')
        api_path = settings.GET_FEE_TYPES_PATH
        url = settings.DOMAIN_NAMES + api_path
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))
        logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        done = time.time()
        logger.info('Reponse_time: {}'.format(done - start_date))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.content))
        logger.info('Finish getting fee types from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                fee_types = json_data.get('data', {})
                return fee_types, True
            else:
                return None, False
        else:
            return None, False

    def _get_bonus_types(self):
        logger.info('Start getting bonus types from backend')
        api_path = settings.GET_BONUS_TYPES_PATH
        url = settings.DOMAIN_NAMES + api_path
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))
        logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        done = time.time()
        logger.info('Reponse_time: {}'.format(done - start_date))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.content))
        logger.info('Finish getting bonus types from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                fee_types = json_data.get('data', {})
                return fee_types, True
            else:
                return None, False
        else:
            return None, False
