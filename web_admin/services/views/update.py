from authentications.utils import get_auth_header
from web_admin.api_settings import SERVICE_GROUP_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from django.contrib import messages
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
import logging
from web_admin.restful_helper import RestfulHelper

logger = logging.getLogger(__name__)


class UpdateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "services/service_update.html"
    logger = logger

    group_required = "CAN_EDIT_SERVICE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        service_id = context['service_id']
        currencies, status1 = self._get_currency_choices()
        service_groups, status2 = self._get_service_group_choices()
        service_detail, status3 = self._get_service_detail(service_id)
        agents, status4 = self._get_agent_types_list()
        if status1 and status2 and status3 and status4:
            context = {
                'currencies': currencies,
                'service_groups': service_groups,
                'service_detail': service_detail,
                'service_id': service_id,
                'agent_types': agents
            }

            return render(request, self.template_name, context)
        else:
            return None

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating Service ==========')
        service_id = kwargs['service_id']
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_name')
        currency = request.POST.get('currency')
        description = request.POST.get('description')
        status = request.POST.get('status')
        display_name_local = request.POST.get('display_name_local')
        image_url = request.POST.get('image_url')
        display_name = request.POST.get('display_name')
        allow_all_agent_types = request.POST.get('allow_all_specific_agent_types')
        cbo_agent_types = request.POST.getlist('cbo_allow_specific_agent_type')
        cbo_agent_types = list(map(int, cbo_agent_types))  # convert list string to list int

        body = {
            'service_group_id': service_group_id,
            'service_name': service_name,
            'currency': currency,
            'description': description,
            'display_name_local': display_name_local,
            'image_url': image_url,
            'display_name': display_name,
            'status': status,
            'apply_to_all_agent_type': True if allow_all_agent_types == 'All' else False,
            'service_agent_type': [] if allow_all_agent_types == 'All' else [{'agent_type_id': x} for x in cbo_agent_types]
        }

        url = api_settings.SERVICE_UPDATE_URL.format(service_id)
        data, success = self._put_method(url, "", logger, body)

        if success:
            self.logger.info('========== Finish updating Service ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            return redirect('services:service_detail', ServiceId=service_id)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )

            currencies, status1 = self._get_currency_choices()
            service_groups, status2 = self._get_service_group_choices()
            agents, status4 = self._get_agent_types_list()

            if status1 and status2 and status4:
                body['service_group_id'] = int(body['service_group_id'])
                context = {
                    'currencies': currencies,
                    'service_groups': service_groups,
                    'service_detail': body,
                    'service_id': service_id,
                    'agent_types': agents
                }
                return render(request, self.template_name, context)


    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _get_agent_types_list(self):
        return self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                 func_description="get agent types list",
                                 logger=logger, params={})

    def _get_currency_choices(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(url, "currency choices", logger)
        if success:
            value = data.get('value', '')
            currency_list = self._get_currency_list(value)
            return currency_list, True
        else:
            return [], True

    def _get_currency_list(self, value):
        result = []
        list = value.split(',')
        for item in list:
            currency = item.split('|')
            result.append(currency)

        return result

    def _get_service_group_choices(self):
        return self._get_method(SERVICE_GROUP_LIST_URL, "service group choices", logger, True)

    def _get_service_detail(self, service_id):
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        return self._get_method(url, "service detail", logger, True)
