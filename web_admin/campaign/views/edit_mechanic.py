import logging
from datetime import datetime

from authentications.utils import get_correlation_id_from_username
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_helper import RestfulHelper

from web_admin import setup_logger, api_settings

logger = logging.getLogger(__name__)


class EditMechanicView(TemplateView, GetHeaderMixin):
    template_name = 'campaign/edit_mechanic.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(request, logger, correlation_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Edit Mechanic page ==========')
        context = super().get_context_data(**kwargs)
        campaign_id = self.kwargs.get('campaign_id')
        mechanic_id = self.kwargs.get('mechanic_id')
        is_success, data = self.__get_mechanic(campaign_id, mechanic_id)
        context['mechanic'] = data

        start_date_time = datetime.strptime(data.get('start_timestamp'), '%Y-%m-%dT%H:%M:%SZ')
        end_date_time = datetime.strptime(data.get('end_timestamp'), '%Y-%m-%dT%H:%M:%SZ')

        context['start_date'] = start_date_time.strftime('%Y-%m-%d')
        context['start_time'] = start_date_time.strftime('%H:%M')
        context['end_date'] = end_date_time.strftime('%Y-%m-%d')
        context['end_time'] = end_date_time.strftime('%H:%M')
        context['trigger_names'] = self.__get_trigger_names()
        context['campaign_id'] = campaign_id
        context['mechanic_id'] = mechanic_id
        self.logger.info('========== Finished showing Edit Mechanic page ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign_id = context.get('campaign_id')
        mechanic_id = context.get('mechanic_id')

        input_start_date = request.POST.get('dtp_start_date')
        input_start_time = request.POST.get('dtp_start_time')
        input_end_date = request.POST.get('dtp_end_date')
        input_end_time = request.POST.get('dtp_end_time')

        start_date_time = datetime.strptime(input_start_date + 'T' + input_start_time, '%Y-%m-%dT%H:%M')
        end_date_time = datetime.strptime(input_end_date + 'T' + input_end_time, '%Y-%m-%dT%H:%M')
        param_start_date = start_date_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        param_end_date = end_date_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            'event_name': request.POST.get('trigger'),
            "start_timestamp": param_start_date,
            "end_timestamp": param_end_date
        }

        is_success, status_code, message = self.__update_mechanic(campaign_id, mechanic_id, params)
        if is_success:
            if message == 'Success':
                messages.success(request, 'Save successfully')
            else:
                messages.warning(request, message)
            return redirect('campaign:mechanic_detail', campaign_id=campaign_id, mechanic_id=mechanic_id)

    def __get_mechanic(self, campaign_id: int, mechanic_id: int) -> tuple:
        url = api_settings.GET_MECHANIC_DETAIL.format(bak_rule_id=campaign_id, mechanic_id=mechanic_id)
        is_success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request,
                                                                           "Get mechanic detail")
        return is_success, data

    def __update_mechanic(self, campaign_id: int, mechanic_id: int, params: dict) -> tuple:
        update_mechanic_url = api_settings.UPDATE_MECHANIC.format(rule_id=campaign_id, mechanic_id=mechanic_id)
        is_success, status_code, message, data = RestfulHelper.send('PUT', update_mechanic_url, params, self.request,
                                                                    'Edit mechanic')
        return is_success, status_code, message

    @staticmethod
    def __get_trigger_names():
        register_customer = {'term': 'register_customer', 'description': 'Register customer'}
        executed_order = {'term': 'executed_order', 'description': 'Executed Order'}
        login = {'term': 'login', 'description': 'Log in'}
        link_bank = {'term': 'created_sof', 'description': 'Create SOF'}
        created_order = {'term': 'create_order', 'description': 'Create Order'}
        limit_reached = {'term': 'limit_reached', 'description': 'Limit Reached'}
        profile_update = {'term': 'update_profile', 'description': 'Profile Update'}
        trigger_names = [register_customer, executed_order, login, link_bank, created_order, limit_reached, profile_update]
        return trigger_names
