from django.conf import settings
from django.shortcuts import redirect, render
from web_admin.mixins import GetChoicesMixin
from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests
import logging
import time

logger = logging.getLogger(__name__)

'''
Author: Leo
History:
- 2017-05-04: ... (Leo)
-- API 1: Load Agent Type       - GET api-gateway/agent/v1/types
-- API 2: Load Currency List    - GET api-gateway/centralize-configuration/v1/scopes/global/currencies
'''


class AgentTypeAndCurrenciesDropDownList(TemplateView):
    def _get_agent_types_list(self):
        url = settings.AGENT_TYPES_LIST_URL

        logger.info('Getting agent types list from backend')
        logger.info('URL: {}'.format(url))
        auth_request = requests.get(url, headers=get_auth_header(self.request.user),
                                    verify=settings.CERT)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        response_json = auth_request.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            result = response_json.get('data', [])
            logger.info('Total count of Agent Types is {}'.format(len(result)))
        else:
            result = []
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
        return result

    def _get_currencies_dropdown(self):
        url = settings.GET_ALL_CURRENCY_URL

        logger.info("Getting preload currency list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        done = time.time()
        logger.info("Response time for get preload currency list is {} sec.".format(done - start_date))

        response_json = response.json()
        print('-----------------{}--------------------'.format(response_json))

        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            try:
                value = response_json['data']['value']
            except:
                return {}
            currencies = value.split(',')
            result = [currency.split("|")[0] for currency in currencies]
            logger.info("Received {} preload currencies".format(len(result)))
        else:
            result = []
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
        return result


'''
Author: Steve Le
History:
- 2017-05-03: Initialize empty Class with template HTML name (Steve Le)
- 2017-05-04: Add logic for Agent registration (Gate Nguyen)
-- API 1: POST api-gateway/agent/v1/agents/{agent_id}/profiles                      [METHOD = _create_agent_profile]
-- API 2: POST api-gateway/agent/v1/agents/{agent_id}/identities                    [METHOD = _create_agent_identity]
-- API 3: POST api-gateway/agent/v1/agents/{agent_id}/sofs/{sof_type}/{currency}    [METHOD = _create_agent_balance]
- 2017-05-05: Corrected API Logic make Agent registration work well (Steve Le)
-- Added logging format and more.
'''


class AgentRegistration(GetChoicesMixin, AgentTypeAndCurrenciesDropDownList):
    template_name = "registration.html"

    def get_context_data(self, *arg, **kwargs):

        # Get API that inherits from parent Class
        logger.info('========== Start get Currency List ==========')
        currencies = self._get_currencies_dropdown()
        logger.info('========== Finished get Currency List ==========')

        logger.info('========== Start get Agent Types List =========')
        agent_types_list = self._get_agent_types_list()
        logging.info('========= Finish get Agent Types List =========')

        result = {
            'currencies': currencies,
            'agent_types_list': agent_types_list,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }

        return result

    def post(self, request, *args, **kwargs):
        logger.info('========== Start Registering Agent Profile ==========')
        agent_profile_reponse, success = self._create_agent_profile(request)
        logger.info('========== Finished Registering Agent Profile ==========')

        agent_id = ''
        if success:
            agent_id = agent_profile_reponse['id']
        else:
            request.session['agent_registration_msg'] = 'Agent registration - profile: something wrong happened!'
            return redirect('agents:agent_registration')

        logger.info('========== Start create agent identity ==========')
        self._create_agent_identity(request, agent_id)
        logger.info('========== Finished create agent identity ==========')

        logger.info('========== Start create agent balance ==========')
        self._create_agent_balance(request, agent_id)
        logger.info('========== Finished create agent balance ==========')

        request.session['agent_registration_msg'] = 'Added agent successfully'

        return redirect('agents:agent_detail', agent_id=agent_id)

    def _create_agent_profile(self, request):

        # Prepare for agent registration.
        password = request.POST.get('password')
        agent_type_id = request.POST.get('agent_type_id')
        parent_id = request.POST.get('parent_id')
        grand_parent_id = request.POST.get('grand_parent_id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        national = request.POST.get('national')
        # Primary Section
        primary_Identify_id = request.POST.get('primary_Identify_id')
        primary_Identify_type = request.POST.get('primary_Identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')
        primary_issue_Date = request.POST.get('primary_issue_date')
        primary_expire_Date = request.POST.get('primary_expire_date')
        # Secondary Section
        secondary_Identify_id = request.POST.get('secondary_Identify_id')
        secondary_Identify_type = request.POST.get('secondary_Identify_type')
        secondary_place_of_issue = request.POST.get('secondary_place_of_issue')
        secondary_issue_Date = request.POST.get('secondary_issue_date')
        secondary_expire_Date = request.POST.get('secondary_expire_date')
        # Contact Info Section
        nationality = request.POST.get('nationality')
        province = request.POST.get('province')
        district = request.POST.get('district')
        commune = request.POST.get('commune')
        address = request.POST.get('address')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        secondary_mobile_number = request.POST.get('secondary_mobile_number')
        tertiary_mobile_number = request.POST.get('tertiary_mobile_number')
        email = request.POST.get('email')
        unique_reference = request.POST.get('unique_reference')
        kyc_status = request.POST.get('kyc_status')
        status = 1  # request.POST.get('status') #TODO: hard fix

        body = {
            'password': password,
            'agent_type_id': agent_type_id,
            'parent_id': parent_id,
            'grand_parent_id': grand_parent_id,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'national': national,
            'primary_Identify_id': primary_Identify_id,
            'primary_Identify_type': primary_Identify_type,
            'primary_place_of_issue': primary_place_of_issue,
            'primary_issue_date': primary_issue_Date,
            'primary_expire_date': primary_expire_Date,
            'secondary_Identify_id': secondary_Identify_id,
            'secondary_Identify_type': secondary_Identify_type,
            'secondary_place_of_issue': secondary_place_of_issue,
            'secondary_issue_date': secondary_issue_Date,
            'secondary_expire_date': secondary_expire_Date,
            'nationality': nationality,
            'province': province,
            'district': district,
            'commune': commune,
            'address': address,
            'primary_mobile_number': primary_mobile_number,
            'secondary_mobile_number': secondary_mobile_number,
            'tertiary_mobile_number': tertiary_mobile_number,
            'email': email,
            'unique_reference': unique_reference,
            'kyc_status': kyc_status,
            'status': status,
        }

        remove = [key for key, value in body.items() if not value]
        for key in remove: del body[key]

        api_path = settings.AGENT_REGISTRATION_URL
        url = settings.DOMAIN_NAMES + api_path

        logger.info('API-Path: {}'.format(api_path))
        logger.info('Params: {}'.format(body))

        start_time = time.time()
        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})

        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            result = response_json.get('data', {}), True
        else:
            result = {}, False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return result

    def _create_agent_identity(self, request, agent_id):

        username = request.POST.get('username')
        password = request.POST.get('password')

        body = {
            'username': username,
            'password': password,
        }

        api_path = settings.CREATE_AGENT_IDENTITY_URL.format(agent_id=agent_id)
        url = settings.DOMAIN_NAMES + api_path

        logger.info('API-Path: {}'.format(api_path))
        # logger.info('Params: {}'.format(body))

        start_time = time.time()
        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            result = True
        else:
            result = False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            request.session['agent_registration_msg'] = 'Agent registration - identity: Something wrong happened!'
            return redirect('agents:agent_registration')
        return result

    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        sof_type = "cash"  # TODO: Hard code for Sof_Type
        body = {}

        api_path = settings.CREATE_AGENT_BALANCE_URL.format(agent_id=agent_id, sof_type=sof_type, currency=currency)
        url = settings.DOMAIN_NAMES + api_path

        logger.info('API-Path: {}'.format(api_path))
        logger.info('Params: {}'.format(body))

        start_time = time.time()
        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            result = True
        else:
            result = False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            request.session['agent_registration_msg'] = 'Agent registration - balance: Something wrong happened!'
            return redirect('agents:agent_registration')
        return result
