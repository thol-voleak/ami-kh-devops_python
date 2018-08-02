from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from multiprocessing.pool import ThreadPool
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin.restful_helper import RestfulHelper


logger = logging.getLogger(__name__)


class CreateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "services/service_create.html"
    logger = logger

    group_required = "CAN_ADD_SERVICE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        choices, success = self._get_service_group_and_currency_choices()
        self.dropdown_data = choices
        if not success:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
            return redirect('services:services_list')

        agents, success = self._get_agent_types_list()
        if not success:
            messages.add_message(
                request,
                messages.INFO,
                'Error when getting agent types!'
            )
            return redirect('services:services_list')

        return render(request, self.template_name, {'choices': choices, 'agent_types': agents})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating service ==========')
        context = super(CreateView, self).get_context_data(**kwargs)
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_name')
        currency = request.POST.get('currency')
        description = request.POST.get('description')
        clone_from = request.POST.get('clone_from')
        clone_service_name = request.POST.get('service_name_hidden')
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
            'apply_to_all_agent_type': True if allow_all_agent_types == 'All' else False,
            'service_agent_type': [] if allow_all_agent_types == 'All' else [{'agent_type_id': x} for x in cbo_agent_types] 
        }

        if clone_from.isdigit():
            body['clone_from'] = clone_from

        url = api_settings.SERVICE_CREATE_URL
        data, success = self._post_method(api_path=url,
                                          func_description="creating service",
                                          logger=logger, params=body)

        if success:
            self.logger.info('========== Finish creating Service ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added service successfully'
            )
            return redirect('services:service_detail', ServiceId=data.get('service_id', ''))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )
            choices, success = self._get_service_group_and_currency_choice()
            context = {'choices': choices, 'body': body, 'clone_service_name': clone_service_name, 'cbo_allow_specific_agent_type': cbo_agent_types}
            return render(request, self.template_name, context)

    def _create_service(self, data):
        url = api_settings.SERVICE_CREATE_URL
        return self._post_method(url, "Service", logger, data)

    def _get_currency_choices(self):
        self.logger.info('========== Start Getting Currency Choices ==========')
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(url, "currency choice", logger)

        if success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
        self.logger.info('========== Finish Getting Currency Choices ==========')
        return result

    def _get_service_group_choices(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        return self._get_method(url, "services group list", logger, True)

    def _get_agent_types_list(self):
        return self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                 func_description="get agent types list",
                                 logger=logger, params={})
 
    def _get_service_group_and_currency_choices(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        self.logger.info('========== Start Getting Service Group Choices ==========')
        service_groups, success_service = self._get_service_group_choices()
        self.logger.info('========== Finish Getting Service Group Choices ==========')
        currencies, success_currency = async_result.get()
        services = self.get_services_list({'paging': False, 'status': 1})
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                       'services': services
                   }, True
        return None, False

    def get_services_list(self, params):
        url = api_settings.SEARCH_SERVICE
        success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request, "searching service", "data.services")
        return data.get('services') if success else []
