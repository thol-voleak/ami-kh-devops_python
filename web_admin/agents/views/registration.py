import logging
from web_admin import api_settings
from datetime import datetime
from django.shortcuts import redirect
from web_admin.mixins import GetChoicesMixin
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Leo
History:
- 2017-05-04: ... (Leo)
-- API 1: Load Agent Type       - GET api-gateway/agent/v1/types
-- API 2: Load Currency List    - GET api-gateway/centralize-configuration/v1/scopes/global/currencies
'''


class AgentTypeAndCurrenciesDropDownList(TemplateView, RESTfulMethods):
    def _get_agent_types_list(self):
        data, success = self._get_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                         func_description="Agent Type List",
                                         logger=logger,
                                         is_getting_list=True)
        return data

    def _get_currencies_dropdown(self):
        data, success = self._get_method(api_path=api_settings.GET_ALL_CURRENCY_URL,
                                         func_description="Agent All Currency List",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            try:
                value = data['value']
                currencies = value.split(',')
                result = [currency.split("|")[0] for currency in currencies]
            except:
                result = []
        else:
            result = []
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
    template_name = "agents/registration.html"

    def get_context_data(self, *arg, **kwargs):

        # Get API that inherits from parent Class
        currencies = self._get_currencies_dropdown()
        agent_types_list = self._get_agent_types_list()

        result = {
            'currencies': currencies,
            'agent_types_list': agent_types_list,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }

        return result

    def post(self, request, *args, **kwargs):
        agent_profile_reponse, success = self._create_agent_profile(request)

        agent_id = ''
        if success:
            agent_id = agent_profile_reponse['id']
        else:
            request.session['agent_registration_msg'] = 'Agent registration - profile: something wrong happened!'
            return redirect('agents:agent_registration')

        self._create_agent_identity(request, agent_id)

        self._create_agent_balance(request, agent_id)

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
        if date_of_birth != '':
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')

        gender = request.POST.get('gender')
        national = request.POST.get('national')
        # Primary Section
        primary_Identify_id = request.POST.get('primary_Identify_id')
        primary_Identify_type = request.POST.get('primary_Identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')

        primary_issue_Date = request.POST.get('primary_issue_date')
        if primary_issue_Date != '':
            primary_issue_Date = datetime.strptime(primary_issue_Date, "%Y-%m-%d")
            primary_issue_Date = primary_issue_Date.strftime('%Y-%m-%dT%H:%M:%SZ')  #1986-01-01T00:00:00Z


        primary_expire_Date = request.POST.get('primary_expire_date')
        if primary_expire_Date != '':
            primary_expire_Date = datetime.strptime(primary_expire_Date, "%Y-%m-%d")
            primary_expire_Date = primary_expire_Date.strftime('%Y-%m-%dT%H:%M:%SZ')
        # Secondary Section
        secondary_Identify_id = request.POST.get('secondary_Identify_id')
        secondary_Identify_type = request.POST.get('secondary_Identify_type')

        secondary_place_of_issue = request.POST.get('secondary_place_of_issue')

        secondary_issue_Date = request.POST.get('secondary_issue_date')
        if secondary_issue_Date != '':
            secondary_issue_Date = datetime.strptime(secondary_issue_Date, "%Y-%m-%d")
            secondary_issue_Date = secondary_issue_Date.strftime('%Y-%m-%dT%H:%M:%SZ')

        secondary_expire_Date = request.POST.get('secondary_expire_date')
        if secondary_expire_Date != '':
            secondary_expire_Date = datetime.strptime(secondary_expire_Date, "%Y-%m-%d")
            secondary_expire_Date = secondary_expire_Date.strftime('%Y-%m-%dT%H:%M:%SZ')

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
            'agent_type_id': agent_type_id,
            'parent_id': parent_id,
            'grand_parent_id': grand_parent_id,
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

        data, success = self._post_method(api_path=api_settings.AGENT_REGISTRATION_URL,
                                          func_description="Agent Profile",
                                          logger=logger, params=body)
        return data, success

    def _create_agent_identity(self, request, agent_id):

        username = request.POST.get('username')
        password = request.POST.get('password')

        body = {
            'username': username,
            'password': password,
        }

        data, success = self._post_method(api_path=api_settings.CREATE_AGENT_IDENTITY_URL.format(agent_id=agent_id),
                                          func_description="Agent Identity",
                                          logger=logger, params=body)
        if success:
            result = True
        else:
            request.session['agent_registration_msg'] = 'Agent registration - identity: Something wrong happened!'
            return redirect('agents:agent_registration')
        return result

    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        sof_type = "cash"  # TODO: Hard code for Sof_Type
        body = {}

        data, success = self._post_method(api_path=api_settings.CREATE_AGENT_BALANCE_URL.format(agent_id=agent_id, sof_type=sof_type, currency=currency),
                                          func_description="Agent Balance",
                                          logger=logger, params=body)

        if success:
            result = True
        else:
            request.session['agent_registration_msg'] = 'Agent registration - balance: Something wrong happened!'
            return redirect('agents:agent_registration')
        return result