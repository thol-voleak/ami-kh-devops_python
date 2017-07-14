from agents.views import AgentAPIService

import logging

from web_admin import api_settings
from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from datetime import datetime
from django.utils import dateparse
from django.http import HttpResponseRedirect

from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)


class AgentUpdate(TemplateView, AgentAPIService):
    template_name = "agents/update.html"
    get_agent_identity_url = "api-gateway/agent/v1/agents/{agent_id}/identities"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(AgentUpdate, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start showing Update Agent page ==========')
        context = super(AgentUpdate, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        agent_types_list, agent_type_status = self.get_agent_types()
        currencies, get_currency_status = self.get_currencies(agent_id)
        agent_profile = self.get_agent_profile(agent_id)

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

        agent_identity, status_get_agent_identity = self.get_agent_identity(agent_id)

        context = {
            'agent_types': agent_types_list,
            'currencies': currencies,
            'agent_profile': agent_profile
        }

        if len(agent_identity['agent_identities']) > 0:
            context.update({'status_get_agent_identity': agent_identity['agent_identities'][0]})

        self.logger.info('========== Finished showing Update Agent page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating agent ==========')
        agent_id = kwargs['agent_id']

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
        primary_Identify_id = request.POST.get('primary_identify_id')
        primary_Identify_type = request.POST.get('primary_identify_type')
        primary_place_of_issue = request.POST.get('primary_place_of_issue')

        primary_issue_Date = request.POST.get('primary_issue_date')
        if primary_issue_Date != '':
            primary_issue_Date = datetime.strptime(primary_issue_Date, "%Y-%m-%d")
            primary_issue_Date = primary_issue_Date.strftime('%Y-%m-%dT%H:%M:%SZ')

        primary_expire_Date = request.POST.get('primary_expire_date')
        if primary_expire_Date != '':
            primary_expire_Date = datetime.strptime(primary_expire_Date, "%Y-%m-%d")
            primary_expire_Date = primary_expire_Date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Secondary Section
        secondary_Identify_id = request.POST.get('secondary_identify_id')
        secondary_Identify_type = request.POST.get('secondary_identify_type')
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
        status = 1  # request.POST.get('status') TODO hard fix

        data = {
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

        data, success = self._put_method(api_path=api_settings.AGENT_UPDATE_PATH.format(agent_id=agent_id),
                                         func_description="Agent",
                                         logger=logger, params=data)
        if success:
            request.session['agent_update_msg'] = 'Updated data successfully'
            previous_page = request.POST.get('previous_page')
            self.logger.info('========== Finished updating agent ==========')
            return HttpResponseRedirect(previous_page)
        self.logger.info('========== Finished updating agent ==========')
        return redirect(request.META['HTTP_REFERER'])
