from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from web_admin.mixins import GetChoicesMixin

import requests
import logging
import time

logger = logging.getLogger(__name__)


class AgentRegistration(TemplateView, GetChoicesMixin):
    template_name = "registration.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start Registering Agent Profile ==========')
        success, data = self._create_agent_profile(request)
        logger.info('========== Finished Registering Agent Profile ==========')

        agent_id = 178 # data['id']

        # logger.info('========== Start create agent identity ==========')
        # self._create_agent_identity(request, agent_id)
        # logger.info('========== Finished create agent identity ==========')
        #
        # logger.info('========== Start create agent balance ==========')
        # success = self._create_agent_balance(request, agent_id)
        # logger.info('========== Finished create agent balance ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Registering Agent successfully'
            )
            # return redirect('agents:agent_detail', AgentId=agent_id)
            return redirect('agents:agent_registration')

    def _create_agent_profile(self, request):
        password = "password"  # request.POST.get('password')
        agent_type_id = 1  # request.POST.get('agent_type_id')
        parent_id = 2  # request.POST.get('parent_id')
        grand_parent_id = 3  # request.POST.get('grand_parent_id')
        bank_name = "TBPPPP"  # request.POST.get('bank_name')
        agent_bank_account = "79304689547298754"  # request.POST.get('agent_bank_account')
        card_id = "1at65bhdfapb"  # request.POST.get('card_id')
        edc_id = "5"  # request.POST.get('edc_id')
        sim_id = "6"  # request.POST.get('sim_id')
        adapter_id = "7"  # request.POST.get('adapter_id')
        battery_id = "8"  # request.POST.get('battery_id')
        edc_app_version = "9"  # request.POST.get('edc_app_version')
        firstname = "TC_EQP_00083_sbirtge firstName"  # request.POST.get('firstname')
        lastname = "TC_EQP_00083_sbirtge lastName"  # request.POST.get('lastname')
        date_of_birth = "19890620"  # request.POST.get('date_of_birth')
        gender = "Male"  # request.POST.get('gender')
        national = "VN"  # request.POST.get('national')
        primary_Identify_id = "primary id "  # request.POST.get('primary_Identify_id')
        primary_Identify_type = "primary type"  # request.POST.get('primary_Identify_type')
        primary_place_of_issue = "Hanoi"  # request.POST.get('primary_place_of_issue')
        primary_issue_Date = "2017-01-01"  # request.POST.get('primary_issue_Date')
        primary_expire_Date = "2017-05-01"  # request.POST.get('primary_expire_Date')
        secondary_Identify_id = "2identifyid"  # request.POST.get('secondary_Identify_id')
        secondary_Identify_type = "2identifyid"  # request.POST.get('secondary_Identify_type')
        tertiary_phone = "2identifytype"  # request.POST.get('tertiary_phone')
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
            return True, json_data.get('data')
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!',
            )
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
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!',
            )
            return redirect('agents:agent_registration')

    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        sofType = "cash"  # hardcode
        body = {} # 'currency': currency

        logger.info("User: {}".format(self.request.user.username))

        url = settings.DOMAIN_NAMES + settings.CREATE_AGENT_BALANCE_URL.format(agent_id=agent_id, sofType=sofType,
                                                                               currency=currency)

        logger.info('Request url: {}'.format(url))
        logger.info('Request body: {}'.format(body))

        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)

        logger.info("Received response with status {}".format(response.status_code))
        logger.info("Response content is {}".format(response.content))

        if response.status_code == 200:
            return True
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!',
            )
            return redirect('agents:agent_registration')
