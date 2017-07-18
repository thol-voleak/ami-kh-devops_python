import logging
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect
from authentications.utils import get_correlation_id_from_username, get_auth_header
logger = logging.getLogger(__name__)


class ListCommandView(TemplateView, RESTfulMethods):
    template_name = "services/command/command_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListCommandView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding service command ==========')

        service_id = kwargs['service_id']
        command_id = request.POST.get('command_id')

        data = {
            'service_id': service_id,
            'command_id': command_id,
        }

        data, success = self._add_service_command(data)
        self.logger.info('========== Finish adding service command ==========')
        if success:
            request.session['add_command_msg'] = 'Added command successfully'
        else:
            request.session['add_failed_msg'] = data

        return redirect(request.META['HTTP_REFERER'])

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _add_service_command(self, data):
        url = api_settings.SERVICE_COMMAND_ADD_URL
        return self._post_method(url, "service command", logger, data)

    def get_context_data(self, **kwargs):
        context = super(ListCommandView, self).get_context_data(**kwargs)
        service_id = context['service_id']

        self.logger.info('========== Start get Services Command List ==========')
        data, service_name = self.get_commands_list(service_id)
        self.logger.info('========== Finished get Services Command List ==========')

        self.logger.info('========== Start get Command List ==========')
        commands_dd_list = self._get_commands_dd_list()
        self.logger.info('========== Finished get Command List ==========')

        context['data'] = data
        context['service_name'] = service_name
        context['command_id'] = commands_dd_list[0]["command_id"]
        context['commands_dd_list'] = commands_dd_list
        context['msg'] = self.request.session.pop('add_command_msg', None)
        context['msg_failed'] = self.request.session.pop('add_failed_msg', None) 
        context['delete_msg'] = self.request.session.pop('delete_command_msg', None)       

        return context

    def get_commands_list(self, service_id):
        url = api_settings.COMMAND_LIST_BY_SERVICE_URL.format(service_id)
        data, success = self._get_method(url, "command list", logger, True)
        detail_url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        service_detail, success = self._get_method(detail_url, "SERVICE DETAIL", logger)
        service_name = service_detail.get("service_name", '')

        return data, service_name

    def _get_commands_dd_list(self):
        url = api_settings.COMMAND_LIST_URL
        data, success = self._get_method(url, "command list", logger, True)
        return data