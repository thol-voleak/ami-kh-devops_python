'''
History:
- 2017-05-03: Initialize empty Class with template HTML name (Steve Le)
- 2017-05-04: Add logic for Agent registration (Gate Nguyen)
-- API 1: POST api-gateway/agent/v1/agents/{agent_id}/profiles                      [METHOD = _create_agent_profile]
-- API 2: POST api-gateway/agent/v1/agents/{agent_id}/identities                    [METHOD = _create_agent_identity]
-- API 3: POST api-gateway/agent/v1/agents/{agent_id}/sofs/{sof_type}/{currency}    [METHOD = _create_agent_balance]
- 2017-05-05: Corrected API Logic make Agent registration work well (Steve Le)
-- Added logging format and more.
'''

import logging

from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from datetime import datetime
from django.shortcuts import redirect, render
from web_admin.mixins import GetChoicesMixin
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import encrypt_text_agent, setup_logger

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentTypeAndCurrenciesDropDownList(TemplateView, RESTfulMethods):
    def _get_agent_types_list(self):
        data, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                         func_description="Agent Type List",
                                         logger=logger)
        newdata = [i for i in data if not i['is_deleted']]
        return newdata

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


class AgentRegistration(GroupRequiredMixin, GetChoicesMixin, AgentTypeAndCurrenciesDropDownList):
    group_required = "CAN_PERFORM_AGENT_REGISTRATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/registration.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentRegistration, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *arg, **kwargs):
        self.logger.info('========== Start showing Create Agent page ==========')
        # Get API that inherits from parent Class
        currencies = self._get_currencies_dropdown()
        agent_types_list = self._get_agent_types_list()

        result = {
            'currencies': currencies,
            'agent_types_list': agent_types_list,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        self.logger.info('========== Finished showing Create Agent page ==========')
        return result

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating agent ==========')
        ### Get data from dropdown list and user input ####
        currency = request.POST.get('currency')
        agent_types_list = self._get_agent_types_list()
        currencies = self._get_currencies_dropdown()
        primary_Identify_id = request.POST.get('primary_Identify_id')
        primary_Identify_type = request.POST.get('primary_Identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth != '':
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')
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
        profile = {
            'parent_id' : request.POST.get('parent_id'),
            'grand_parent_id': request.POST.get('grand_parent_id'),
            'firstname': request.POST.get('firstname'),
            'lastname': request.POST.get('lastname'),
            'gender': request.POST.get('gender'),
            'national': request.POST.get('national'),
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
            'nationality': request.POST.get('nationality'),
            'province' : request.POST.get('province'),
            'district' : request.POST.get('district'),
            'commune' : request.POST.get('commune'),
            'address' : request.POST.get('address'),
            'primary_mobile_number' : request.POST.get('primary_mobile_number'),
            'secondary_mobile_number' : request.POST.get('secondary_mobile_number'),
            'tertiary_mobile_number' : request.POST.get('tertiary_mobile_number'),
            'email' : request.POST.get('email'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'currency': request.POST.get('currency'),
            'unique_reference': request.POST.get('unique_reference')
        }
        identity = {
            "username": request.POST.get('username'),
            "password": request.POST.get('password'),
        }
        ##########################################

        ######## Fail case create agent profile ###############
        agent_profile_reponse, success = self._create_agent_profile(request)
        context = {
            'agent_types_list': agent_types_list,
            'currencies': currencies,
            'profile': profile,
            'identity': identity,
            'msg': agent_profile_reponse
        }
        agent_id = ''
        if success:
            agent_id = agent_profile_reponse['id']
        else:
            self.logger.info('========== Finished creating agent ==========')
            return render(request, self.template_name, context)

        ####### Fail case agent identity ############
        agent_balance, success = self._create_agent_balance(request, agent_id)
        if success:
            request.session['agent_registration_msg'] = 'Added agent successfully'
            self.logger.info('========== Finished creating agent ==========')
            return redirect('agents:agent_detail', agent_id=agent_id)
        else:
            self.logger.info('========== Finished creating agent ==========')
            return render(request, self.template_name, context)

    def _create_agent_profile(self, request):

        # Prepare for agent registration.
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

        profile = {
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

        username = request.POST.get('username')
        password = request.POST.get('password')
        password = encrypt_text_agent(password)

        identity = {
            'username': username,
            'password': password
        }

        body = {
            'profile': profile,
            'identity': identity
        }

        data, success = self._post_method(api_path=api_settings.AGENT_REGISTRATION_URL,
                                          func_description="Agent Profile",
                                          logger=logger, params=body)
        return data, success

    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        # sof_type = "cash"  # TODO: Hard code for Sof_Type
        body = {'currency': currency}
        api_path = api_settings.CREATE_AGENT_BALANCE_URL.format(agent_id=agent_id)

        data, success = self._post_method(api_path=api_path,
                                          func_description="Agent Balance",
                                          logger=logger, params=body)
        return data, success