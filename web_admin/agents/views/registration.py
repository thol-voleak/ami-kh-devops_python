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
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin

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


class AgentRegistration(GroupRequiredMixin, AgentTypeAndCurrenciesDropDownList, GetHeaderMixin):
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

        status = 1  # request.POST.get('status') #TODO: hard fix
        agent_types_list = self._get_agent_types_list()
        currencies = self._get_currencies_dropdown()

        # basic info session
        agent_type_id = request.POST.get('agent_type_id')
        parent_id = request.POST.get('parent_id')
        grand_parent_id = request.POST.get('grand_parent_id')
        currency = request.POST.get('currency')
        unique_reference = request.POST.get('unique_reference')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password = encrypt_text_agent(password)
        # basic info session

        # Personal Details session    
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth != '':
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')      
        gender = request.POST.get('gender')
        national = request.POST.get('national')
        # Personal Details session

        # Primary Identify session
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
        # Primary Identify session

        # Secondary Identity Section
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
        
        kyc_status = request.POST.get('kyc_status')  
        # Secondary Identity Section

        # Contact Info Section
        nationality = request.POST.get('nationality')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        secondary_mobile_number = request.POST.get('secondary_mobile_number')
        tertiary_mobile_number = request.POST.get('tertiary_mobile_number')
        email = request.POST.get('email')
        # Contact Info Section
        
        
        
        #current address session
        current_province = request.POST.get('current_province')
        current_district = request.POST.get('current_district')
        current_commune = request.POST.get('current_commune')
        current_address = request.POST.get('current_address')
        current_country = request.POST.get('current_country')
        current_landmark = request.POST.get('current_landmark')
        current_longitude = request.POST.get('current_longitude')
        current_latitude = request.POST.get('current_latitude')
        #current address session

        #permanent address
        is_current_address_same_permanent_address = request.POST.get('is-permanent-same-current')
        if is_current_address_same_permanent_address:
            permanent_address = current_address
            permanent_district = current_district
            permanent_province = current_province
            permanent_commune = current_commune
            permanent_country = current_country
            permanent_landmark = current_landmark
            permanent_longitude = current_longitude
            permanent_latitude = current_latitude
        else:
            permanent_address = request.POST.get('permanent_address')
            permanent_district = request.POST.get('permanent_district')
            permanent_province = request.POST.get('permanent_province')
            permanent_commune = request.POST.get('permanent_commune')
            permanent_country = request.POST.get('permanent_country')
            permanent_landmark = request.POST.get('permanent_landmark')
            permanent_longitude = request.POST.get('permanent_longitude')
            permanent_latitude = request.POST.get('permanent_latitude')
        #permanent address

        # bank section
        bank = {
            'name' : request.POST.get('bank_name'),
            'branch_city' : request.POST.get('bank_branch_city'),
            'branch_area' : request.POST.get('bank_branch_area'),
            'account_number' : request.POST.get('bank_account_number')
        }

        # contract section
        contract = {
            'type' : request.POST.get('contract_type'),
            'sign_date' : request.POST.get('contract_sign_date'),
            'number' : request.POST.get('contract_number'),
            'issue_date' : request.POST.get('contract_issue_date'),
            'extended_type' : request.POST.get('extension_type'),
            'expired_date' : request.POST.get('contract_expiry_date'),
            'day_of_period_reconciliation': request.POST.get('notification_alert')
        }
        # contract section

        profile = {
            'agent_type_id': agent_type_id,
            'parent_id': parent_id,
            'grand_parent_id': grand_parent_id,
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
            'province': current_province,
            'district': current_district,
            'commune': current_commune,
            'address': current_address,
            'primary_mobile_number': primary_mobile_number,
            'secondary_mobile_number': secondary_mobile_number,
            'tertiary_mobile_number': tertiary_mobile_number,
            'email': email,
            'unique_reference': unique_reference,
            'kyc_status': kyc_status,
            'status': status,
            'permanent_address': permanent_address,
            'permanent_district': permanent_district,
            'permanent_province': permanent_province,
            'permanent_commune': permanent_commune,
            'permanent_country': permanent_country,
            'permanent_landmark': permanent_landmark,
            'permanent_longitude': permanent_longitude,
            'permanent_latitude': permanent_latitude,
            'country': current_country,
            'landmark': current_landmark,
            'longitude': current_longitude,
            'latitude': current_latitude,
            'bank': bank,
            'contract': contract
        }

        identity = {
            'username': username,
            'password': password
        }

        body = {
            'profile': profile,
            'identity': identity
        }
        is_success, status_code, status_message, agent_profile_reponse = RestFulClient.post(
                                                    url= api_settings.AGENT_REGISTRATION_URL,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        identity = {'username':username}
        body = {
            'profile': profile,
            'identity': identity
        }
        self.logger.info("Params: {} ".format(body))
        context = {
            'agent_types_list': agent_types_list,
            'currencies': currencies,
            'profile': profile,
            'identity': identity,
            'msgs': {
                'get_msg': status_message,
            }
        }
        agent_id = ''
        if is_success:
            agent_id = agent_profile_reponse['id']
            agent_balance, success = self._create_agent_balance(request, agent_id)
            self.logger.info('========== Finished creating agent ==========')
            if success:
                request.session['agent_registration_msg'] = 'Added agent successfully'
                return redirect('agents:agent_detail', agent_id=agent_id)
            elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                return render(request, self.template_name, context)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        else:
            self.logger.info('========== Finished creating agent ==========')
            return render(request, self.template_name, context)


    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        # sof_type = "cash"  # TODO: Hard code for Sof_Type
        body = {'currency': currency,
                'user_id': agent_id,
                'user_type_id': 2}  #TODO: Hard code for agent_type
        api_path = api_settings.CREATE_AGENT_BALANCE_URL

        is_success, status_code, status_message, data = RestFulClient.post(
                                                    url= api_path,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        return data, is_success