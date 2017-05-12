from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from datetime import datetime
from django.utils import dateparse

from django.utils import formats
from django.contrib import messages

import requests, time, logging

logger = logging.getLogger(__name__)

'''
Author: Steve Le
History:
# 2017-05-04
- Init with basic template name "update.html"
# 2017-05-05
-- Load Data
- API 3: GET /api-gateway/agent/v1/agents/{agent_id}
'''
class AgentUpdate( TemplateView ):

    template_name = "update.html"

    def get(self, request, *args, **kwargs):

        context = super(AgentUpdate, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        # MASTER DATA
        # API 1: Get Agent Types List
        agent_types_list = self._get_agent_types()

        # API 2: Get Currencies List
        currencies = self._get_currencies()

        # LOAD DATA
        # API 3: Get Agent Profile
        agent_profile = self._get_agent_profile(agent_id)

        # Format dates
        if agent_profile['date_of_birth'] is not None:
            date_of_birth = dateparse.parse_datetime(agent_profile['date_of_birth'])
            agent_profile['date_of_birth'] = date_of_birth

        if agent_profile['primary_issue_date'] is not None:
            primary_issue_date = dateparse.parse_datetime(agent_profile['primary_issue_date'])
            agent_profile['primary_issue_date'] = primary_issue_date

        if agent_profile['primary_expire_date'] is not None:
            primary_expire_date = dateparse.parse_datetime(agent_profile['primary_expire_date'])
            agent_profile['primary_expire_date'] = primary_expire_date

        if agent_profile['secondary_issue_date'] is not None:
            secondary_issue_date = dateparse.parse_datetime(agent_profile['secondary_issue_date'])
            agent_profile['secondary_issue_date'] = secondary_issue_date

        if agent_profile['secondary_expire_date'] is not None:
            secondary_expire_date = dateparse.parse_datetime(agent_profile['secondary_expire_date'])
            agent_profile['secondary_expire_date'] = secondary_expire_date

        context = {
            'agent_types': agent_types_list,
            'currencies': currencies,
            'agent_profile': agent_profile
        }

        return render(request, self.template_name, context)

    '''
    Author: Steve Le
    # 2017-05-05
    '''
    def _get_agent_profile(self, agent_id):
        logger.info('========== Start getting agent detail ========== ')

        api_path = settings.AGENT_DETAIL_PATH.format(agent_id=agent_id)
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: agent_id = {} ".format(agent_id))

        headers = get_auth_header(self.request.user)

        # Do request
        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()
        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        # Get data
        response_json = response.json()
        status = response_json.get('status', {})

        # Validate data response
        if not isinstance(status, dict):
            status = {}

        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', {})
        else:
            data = {}
            logger.info("Getting agent detail got error.")
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        logger.info('========== Finish getting agent detail ========== ')
        return data

    '''
    Author: Steve Le
    History:
    # 2017-05-08
    -- Load Master Data
    - API 1: GET /api-gateway/agent/v1/types
    '''
    def _get_agent_types(self):
        logger.info('========== Start getting agent types list ========== ')

        api_path = settings.GET_AGENT_TYPES_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: {} ")

        headers = get_auth_header(self.request.user)

        # Do request
        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()
        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        # Get data
        response_json = response.json()
        status = response_json.get('status', {})

        # Validate data response
        if not isinstance(status, dict):
            status = {}

        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', [])
        else:
            data = []
            logger.info("Getting agent types list got error.")
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        logger.info('========== Finish getting agent types list ========== ')
        return data

    '''
    Author: Steve Le
    History:
    # 2017-05-09
    -- Load Master Data
    - API 2: GET /api-gateway/centralize-configuration/v1/scopes/global/configurations/currency
    '''
    def _get_currencies(self):
        logger.info('========== Start getting currencies list ========== ')

        api_path = settings.GET_CURRENCIES_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: {} ")

        headers = get_auth_header(self.request.user)

        # Do request
        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()
        logger.info("Response_time: {} sec.".format(end_time - start_time))
        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))

        # Get data
        response_json = response.json()
        status = response_json.get('status', {})

        # Validate data response
        if not isinstance(status, dict):
            status = {}

        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')

        if code == "success":
            data = response_json.get('data', [])
            values = data.get('value', '')
            currencies = map(lambda x: x.split('|'), values.split(','))
        else:
            currencies = []
            logger.info("Getting currencies got error.")
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        logger.info('========== Finish getting currencies list ========== ')
        return currencies

    def post(self, request, *args, **kwargs):
        logger.info('========== Start updating Agent ==========')
        agent_id = kwargs['agent_id']

        agent_type_id = request.POST.get('agent_type_id')
        parent_id = request.POST.get('parent_id')
        # grand_parent_id = 3  # request.POST.get('grand_parent_id')  # TODO: Hard code for waiting new API
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        national = request.POST.get('national')
        # Primary Section
        primary_Identify_id = request.POST.get('primary_identify_id')
        primary_Identify_type = request.POST.get('primary_identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')
        primary_issue_Date = request.POST.get('primary_issue_date')
        primary_expire_Date = request.POST.get('primary_expire_date')
        # Secondary Section
        secondary_Identify_id = request.POST.get('secondary_identify_id')
        secondary_Identify_type = request.POST.get('secondary_identify_type')
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
        status = 1 # request.POST.get('status') TODO hard fix

        data = {
            'agent_type_id': agent_type_id,
            'parent_id': parent_id,
            'firstname': firstname,
            'lastname': lastname,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'national': national,
            'primary_identify_id': primary_Identify_id,
            'primary_identify_type': primary_Identify_type,
            'primary_place_of_issue': primary_place_of_issue,
            'primary_issue_date': primary_issue_Date,
            'primary_expire_date': primary_expire_Date,
            'secondary_identify_id': secondary_Identify_id,
            'secondary_identify_type': secondary_Identify_type,
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

        date_fields = ["date_of_birth", "primary_issue_date", "primary_expire_date", "secondary_issue_date",
                  "secondary_expire_date"]
        for key in date_fields:
            if not data.get(key, ''):
                del data[key]

        for key, value in data.items():
            if not value:
                data[key] = ''

        data, success = self._update_agent(agent_id, data)
        if success:
            request.session['agent_update_msg'] = 'Updated data successfully'
            return redirect('agents:agent-list')
        return redirect(request.META['HTTP_REFERER'])

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _update_agent(self, agent_id, data):
        api_path = settings.AGENT_UPDATE_PATH.format(agent_id=agent_id)
        url = settings.DOMAIN_NAMES + api_path

        logger.info('Updating Agent - API-Path: {path}'.format(path=api_path))
        logger.info('Updating Agent - Params: {}'.format(data))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(),
                                json=data, verify=settings.CERT)
        done = time.time()
        logger.info('Getting Agent detail - Response_time: {}'.format(done - start_date))
        logger.info('Getting Agent detail - Response_code: {}'.format(response.status_code))
        logger.info('Getting Agent detail - Response_content: {}'.format(response.text))

        response_json = response.json()
        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            result = response_json.get('data', {}), True
            logger.info('========== Finished updating Agent ==========')
        else:
            logger.info('========== Finished updating Agent ==========')
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            result = None, False
        return result
