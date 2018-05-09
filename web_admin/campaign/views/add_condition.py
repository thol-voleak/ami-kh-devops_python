from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC, CREATE_CONDITION, CREATE_COMPARISON, CREATE_REWARD, CREATE_LIMITATION, CREATE_FILTER, CREATE_RESET_FILTER
from web_admin import setup_logger, RestFulClient
from web_admin.restful_helper import RestfulHelper
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from campaign.models import terms_mapping
from django.views.generic.base import TemplateView
from django.http import JsonResponse

import logging

from web_admin.utils import build_logger

logger = logging.getLogger(__name__)


class AddCondition(TemplateView, GetHeaderMixin):
    template_name = "campaign/add_condition.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(self.request, __name__)
        return super(AddCondition, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Condition page ==========')
        context = super(AddCondition, self).get_context_data(**kwargs)

        all_terms = list(terms_mapping.objects.values('term', 'description'))
        detail_names = self._filter_detail_names(all_terms)
        # trigger = self._filter_trigger(all_terms)

        ops = {
            'detail_names': detail_names,
            # 'trigger': trigger
        }

        context.update(ops)
        self.logger.info('========== Finished showing Add Condition page ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AddCondition, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']

        condition_type = request.POST.get('condition_type')

        if condition_type == 'event_detail':
            params = {'filter_type': condition_type}
            success, data, message = self.create_condition(campaign_id, mechanic_id, params)
            if not success:
                return JsonResponse({"status": "fail", "msg": message})

            condition_id = data['id']

            params = {
                'key_name': request.POST.get("detail_name"),
                'key_value_type': request.POST.get("key_value_type"),
                'operator': request.POST.get("operator"),
                'key_value': request.POST.get("key_value")
            }
            success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return JsonResponse({"status": "fail", "msg": message})

        messages.success(request, 'Save successfully')
        return JsonResponse({"status": "success"})

    def create_condition(self, campaign_id, mechanic_id, params):
        add_condition_url = CREATE_CONDITION.format(rule_id=campaign_id, mechanic_id=mechanic_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_condition_url, params, self.request, "creating condition")
        return success, data, message

    def create_comparison(self, campaign_id, mechanic_id, condition_id, params):
        add_comparison_url = CREATE_COMPARISON.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_comparison_url, params, self.request, "creating comparison")

        return success, data, message

    def create_filter(self, campaign_id, mechanic_id, condition_id, params):
        add_filter_url = CREATE_FILTER.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_filter_url, params, self.request, "creating filter")
        return success, data, message

    def create_reset_filter(self, campaign_id, mechanic_id, condition_id, params):
        add_reset_filter_url = CREATE_RESET_FILTER.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_reset_filter_url, params, self.request, "creating reset filter")
        return success, data, message

    def _filter_detail_names(self, data):
        filtered = [v for v in data if
                    (v.get('term') != 'register_customer') and (v.get('term') != 'executed_order') and (v.get('term') != 'login')]
        username = {'term': 'username', 'description': ''}
        is_login_success = {'term': 'is_login_success', 'description': ''}
        filtered.extend((username, is_login_success))
        return filtered

    def _filter_trigger(self, data):
        filtered = [v for v in data if
                    ((v.get('term') == 'register_customer') or (v.get('term') == 'executed_order') or (v.get('term') == 'login'))]
        link_bank = {'term': 'created_sof', 'description': 'Link Bank'}
        created_order = {'term': 'create_order', 'description': 'Create Order'}
        limit_reached = {'term': 'limit_reached', 'description': 'Limit Reached'}
        filtered.extend([link_bank, created_order, limit_reached])
        return filtered