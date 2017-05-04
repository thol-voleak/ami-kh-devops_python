from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from web_admin.mixins import GetChoicesMixin
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests
import logging
import time

logger = logging.getLogger(__name__)


class AgentTypeAndPreloadCurrenciesDropDownList(TemplateView):

    def _get_agent_types_list(self):
        url = settings.AGENT_TYPES_LIST_URL

        logger.info('Getting agent types list from backend')
        logger.info('URL: {}'.format(url))
        auth_request = requests.get(url, headers=get_auth_header(self.request.user),
                                    verify=settings.CERT)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Total count of Agent Types is {}'.format(len(data)))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))


    def _get_preload_currencies_dropdown(self):
        url = settings.GET_ALL_PRELOAD_CURRENCY_URL

        logger.info("Getting preload currency list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        done = time.time()
        json_data = response.json()
        logger.info("Response time for get preload currency list is {} sec.".format(done - start_date))
        data = json_data.get('data')
        if response.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info("Received {} preload currencies".format(len(json_data['data'])))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))


class AgentRegistration(GetChoicesMixin, AgentTypeAndPreloadCurrenciesDropDownList):
    template_name = "registration.html"


    def get_context_data(self, *arg, **kwargs):
        logger.info('========== Start get Currency List ==========')
        preload_currencies = self._get_preload_currencies_dropdown()
        logger.info('========== Finished get Currency List ==========')

        logger.info('========== Start get Agent Types List =========')
        agent_types_list = self._get_agent_types_list()

        #print('----------------------------------------- {}'.format(agent_types_list))
        logging.info('========= Finish get Agent Types List =========')

        result = {'preload_currencies': preload_currencies,
                  'agent_types_list': agent_types_list,
                  'msg': self.request.session.pop('agent_registration_msg', None)}
        return result


    def post(self, request, *args, **kwargs):
        logger.info('========== Start Registering Agent Profile ==========')
        data = self._create_agent_profile(request)
        logger.info('========== Finished Registering Agent Profile ==========')

        agent_id = 1 # data['id']

        logger.info('========== Start create agent identity ==========')
        self._create_agent_identity(request, agent_id)
        logger.info('========== Finished create agent identity ==========')

        logger.info('========== Start create agent balance ==========')
        success = self._create_agent_balance(request, agent_id)
        logger.info('========== Finished create agent balance ==========')

        request.session['agent_registration_msg'] = 'Registering Agent successfully'
        return redirect('agents:agent_detail', agent_id=agent_id)

    def _create_agent_profile(self, request):
        password = request.POST.get('password')
        agent_type_id = request.POST.get('agent_type_id')
        parent_id = request.POST.get('parent_id')
        grand_parent_id = 3  # request.POST.get('grand_parent_id')
        bank_name =  request.POST.get('bank_name')
        agent_bank_account =  request.POST.get('agent_bank_account')
        card_id = request.POST.get('card_id')
        edc_id = request.POST.get('edc_id')
        sim_id =  request.POST.get('sim_id')
        adapter_id = request.POST.get('adapter_id')
        battery_id = request.POST.get('battery_id')
        edc_app_version = request.POST.get('edc_app_version')
        firstname =  request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        national = request.POST.get('national')
        primary_Identify_id = request.POST.get('primary_Identify_id')
        primary_Identify_type = request.POST.get('primary_Identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')
        primary_issue_Date = request.POST.get('primary_issue_Date')
        primary_expire_Date = request.POST.get('primary_expire_Date')
        secondary_Identify_id = request.POST.get('secondary_Identify_id')
        secondary_Identify_type = request.POST.get('secondary_Identify_type')
        tertiary_phone = request.POST.get('tertiary_phone')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name')
        shop_product = request.POST.get('shop_product')
        kyc_status = request.POST.get('kyc_status')
        status = request.POST.get('status')

        body = {
            'password': password,
            'agent_type_id': agent_type_id,
            'parent_id': parent_id,
            'grand_parent_id': grand_parent_id,
            'password': password,
            'bank_name': bank_name,
            'agent_bank_account': agent_bank_account,
            'card_id': card_id,
            'edc_id': edc_id,
            'sim_id': sim_id,
            'adapter_id': adapter_id,
            'battery_id': battery_id,
            'edc_app_version': edc_app_version,
            'firstname': firstname,
            'lastname': lastname,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'national': national,
            'primary_Identify_id': primary_Identify_id,
            'primary_Identify_type': primary_Identify_type,
            'primary_place_of_issue': primary_place_of_issue,
            'primary_issue_Date': primary_issue_Date,
            'primary_expire_Date': primary_expire_Date,
            'secondary_Identify_id': secondary_Identify_id,
            'secondary_Identify_type': secondary_Identify_type,
            'tertiary_phone': tertiary_phone,
            'email': email,
            'shop_name': shop_name,
            'shop_product': shop_product,
            'kyc_status': kyc_status,
            'status': status,
        }
        logger.info("User: {}".format(self.request.user.username))

        url = settings.DOMAIN_NAMES + settings.AGENT_REGISTRATION_URL

        logger.info('Request url: {}'.format(url))
        logger.info('Request body: {}'.format(body))
        start_time = time.time()

        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response time: {} sec.".format(end_time - start_time))
        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))

        json_data = response.json()
        if response.status_code == 200:
            return json_data.get('data')
        else:
            request.session['agent_registration_msg'] = 'Something wrong happened!'
            return redirect('agents:agent_registration')

    def _create_agent_identity(self, request, agent_id):

        username = request.POST.get('username')
        password = request.POST.get('password')
        body = {
            'username': username,
            'password': password,
        }

        logger.info("User: {}".format(self.request.user.username))

        url = settings.DOMAIN_NAMES + settings.CREATE_AGENT_IDENTITY_URL.format(agent_id=agent_id)

        logger.info('Request url: {}'.format(url))
        logger.info('Request body: {}'.format(body))

        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)

        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))

        if response.status_code == 200:
            return True
        else:
            request.session['agent_registration_msg'] = 'Something wrong happened!'
            return redirect('agents:agent_registration')

    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        sof_type = "cash"  # hardcode
        body = {}

        logger.info("User: {}".format(self.request.user.username))

        url = settings.DOMAIN_NAMES + settings.CREATE_AGENT_BALANCE_URL.format(agent_id=agent_id, sof_type=sof_type,
                                                                               currency=currency)

        logger.info('Request url: {}'.format(url))
        logger.info('Request body: {}'.format(body))

        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)

        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))

        if response.status_code == 200:
            return True
        else:
            request.session['agent_registration_msg'] = 'Something wrong happened!'
            return redirect('agents:agent_registration')




