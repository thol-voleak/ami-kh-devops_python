import time
from multiprocessing import Process, Manager

from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render
from authentications.utils import get_auth_header

from web_admin.get_header_mixins import GetHeaderMixin
import requests
import logging

logger = logging.getLogger(__name__)


class UpdateView(TemplateView, GetHeaderMixin):
    template_name = "tier/update.html"

    def get(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        tier_id = context['fee_tier_id']
        tier_to_update = self._get_tier_detail(tier_id)
        for i in tier_to_update:
            if tier_to_update[i] is None:
                tier_to_update[i] = 'Non'

        context['update_tier'] = tier_to_update
        service_id = context['service_id']
        command_id = context['command_id']

        manager = Manager()
        return_dict = manager.dict()

        process_get_tier_condition = Process(target=self._get_tier_condition,
                                             args=(1, return_dict))
        process_get_tier_condition.start()
        process_get_amount_types = Process(target=self._get_amount_types,
                                           args=(2, return_dict))
        process_get_amount_types.start()
        process_get_service_detail = Process(target=self._get_service_detail,
                                             args=(3, return_dict, service_id))
        process_get_service_detail.start()
        process_get_command_name = Process(target=self._get_command_name,
                                           args=(4, return_dict, command_id))
        process_get_command_name.start()

        process_get_fee_types = Process(target=self._get_fee_types, args=(5, return_dict))
        process_get_fee_types.start()
        process_get_bonus_types = Process(target=self._get_bonus_types, args=(6, return_dict))
        process_get_bonus_types.start()

        process_get_tier_condition.join()
        process_get_amount_types.join()
        process_get_service_detail.join()
        process_get_command_name.join()
        process_get_fee_types.join()
        process_get_bonus_types.join()

        tier_conditions, status1 = return_dict[1]
        amount_types, status2 = return_dict[2]
        service_detail, status3 = return_dict[3]
        command_name, status4 = return_dict[4]
        fee_types, status5 = return_dict[5]
        bonus_types, status6 = return_dict[6]

        if process_get_tier_condition.is_alive():
            process_get_tier_condition.terminate()

        if process_get_amount_types.is_alive():
            process_get_amount_types.terminate()

        if process_get_service_detail.is_alive():
            process_get_service_detail.terminate()

        if process_get_command_name.is_alive():
            process_get_command_name.terminate()

        if process_get_fee_types.is_alive():
            process_get_fee_types.terminate()

        if process_get_bonus_types.is_alive():
            process_get_bonus_types.terminate()

        if status1 and status2 and status3 and status4 and status5 and status6:
            context.update({
                'conditions': tier_conditions,
                'fee_types': fee_types,
                'bonus_types': bonus_types,
                'amount_types': amount_types,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'update_tier': tier_to_update,
            })
        return render(request, self.template_name, context)

    def _get_tier_detail(self, tier_id):
        url = (settings.DOMAIN_NAMES + settings.TIER_PATH).format(tier_id)
        logger.info('Start getting tier detail')
        logger.info('API-Path: {};'.format(url))
        start = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        finish = time.time()
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {};'.format(response.content))
        logger.info('Response_time: {} sec.'.format(finish - start))
        logger.info('Finished getting tier detail')
        data = {}
        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get('data', {})

        return data


    def _get_tier_condition(self, procnum, dict):
        logger.info('Start getting fee tier condition from backend')
        url = settings.FEE_TIER_CONDITION_URL
        logger.info('Request URL: {};'.format(url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Response code: {};".format(response.status_code))
        logger.info("Response content: {};".format(response.content))
        logger.info('Finish getting fee tier condition from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                conditions = json_data.get('data', {})
                dict[procnum] = conditions, True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_amount_types(self, procnum, dict):
        logger.info('Start getting amount types from backend')

        url = settings.AMOUNT_TYPES_URL
        logger.info('Request url: {}'.format(url))

        logger.info('Get amount types from backend')
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        logger.info("Response code: {};".format(response.status_code))
        logger.info("Response content {};".format(response.content))
        logger.info('Finish getting amount types from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                dict[procnum] = json_data.get('data', {}), True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_service_detail(self, procnum, dict, service_id):
        logger.info('Start getting service detail {} from backend'.format(service_id))

        url = settings.SERVICE_DETAIL_URL.format(service_id)
        logger.info('Request url: {}'.format(url))

        headers = get_auth_header(self.request.user)

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        done = time.time()
        logger.info("Response time:{} sec.".format(done - start_date))
        logger.info("Response code {};".format(response.status_code))
        logger.info("Response content: {};".format(response.content))
        logger.info('Finish getting service detail {} from backend'.format(service_id))

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                dict[procnum] = json_data.get('data', {}), True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_command_name(self, procnum, dict, command_id):
        logger.info('Start getting commands list from backend')

        url = settings.COMMAND_LIST_URL
        logger.info('Request url: {}'.format(url))

        headers = get_auth_header(self.request.user)

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        done = time.time()
        logger.info("Response time:{} sec.".format(done - start_date))
        logger.info("Response code: {};".format(response.status_code))
        logger.info("Response content {};".format(response.content))
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
                        dict[procnum] = command_name, True
                        return None

                dict[procnum] = 'Unknown', True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_fee_types(self, procnum, dict):
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
                dict[procnum] = fee_types, True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_bonus_types(self, procnum, dict):
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
                dict[procnum] = fee_types, True
            else:
                dict[procnum] = None, False
        else:
            dict[procnum] = None, False

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers


    def post(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        logger.info('========== Start editing tier for service command ==========')
        command_id = context['command_id']
        service_id = context['service_id']
        service_command_id = context['service_command_id']

        data = {
            "fee_tier_condition": request.POST.get('condition'),
            "condition_amount": request.POST.get('condition_amount'),
            "fee_type": request.POST.get('fee_type'),
            "fee_amount": request.POST.get('fee_amount'),
            "bonus_type": request.POST.get('bonus_type'),
            "bonus_amount": request.POST.get('bonus_amount'),
            "amount_type": request.POST.get('amount_type'),
        }

        if data['bonus_type'] == "Flat value":
            data['amount_type'] = ''

        fee_tier_id = context['fee_tier_id']

        success = self._edit_tier(fee_tier_id, data)
        logger.info('========== Finish editing tier for service command ==========')
        if success:
            request.session['edit_tier_msg'] = 'Edited data successfully'
        return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id,
                        service_command_id=service_command_id)

    def _edit_tier(self, fee_tier_id, data):
        url = (settings.DOMAIN_NAMES + settings.TIER_PATH).format(fee_tier_id)

        logger.info('API-Path: {};'.format(url))
        logger.info('Params: {};'.format(data))
        start = time.time()
        response = requests.put(url, headers=self._get_headers(),
                                json=data, verify=settings.CERT)
        finish = time.time()
        logger.info("Response_code: {};".format(response.status_code))
        logger.info("Response_content: {};".format(response.content))
        logger.info("Response_time: {} sec.".format(finish - start))

        if response.status_code == 200:
            response_json = response.json()
            status = response_json['status']
            if status['code'] == "success":
                return True
        return False