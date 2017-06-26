import logging
from web_admin import api_settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View, TemplateView
from web_admin.restful_methods import RESTfulMethods
from django.contrib import messages
from services.views.update import UpdateView
from web_admin.utils import setup_logger
logger = logging.getLogger(__name__)


class DeleteCommand(UpdateView, RESTfulMethods):
    template_name = "services/command/command_delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DeleteCommand, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting Service Command ==========')
        context = super(DeleteCommand, self).get_context_data(**kwargs)
        service_detail, success = self._get_service_detail(context['service_id'])
        context['command'] = kwargs.get('command')
        command_name, success = self._get_command_name(context['command_id'])
        context.update({
            'service_name': service_detail.get('service_name', 'unknown'),
            'command_name': command_name,
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting Service Command ==========')
        service_command_id = kwargs['service_command_id']
        service_id = kwargs['service_id']
        success = self._delete_service_command(service_command_id)
        self.logger.info('========== Finish deleting Service Command ==========')

        if success:
            request.session['delete_command_msg'] = 'Deleted data successfully'
            return redirect('services:command_list', service_id=service_id)
        else:
            context = super(DeleteCommand, self).get_context_data(**kwargs)
            service_detail, success = self._get_service_detail(context['service_id'])
            context['command'] = kwargs.get('command')
            command_name, success = self._get_command_name(context['command_id'])
            context.update({
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'delete_command_msg_failed': 'Delete data failed',
            })
            return render(request, self.template_name, context)

    def _get_command_name(self, command_id):
        commands_list, status = self._get_method(api_settings.COMMAND_LIST_URL,
                                                  func_description="Commands List",
                                                  logger=logger)
        if status:
            command_name = None
            my_id = int(command_id)
            for x in commands_list:
                if x['command_id'] == my_id:
                    command_name = x['command_name']
                    return command_name, True
            return 'Unknown', True
        else:
            return None, False

    def _delete_service_command(self, service_command_id):
        api_path = api_settings.SERVICE_COMMAND_DELETE_PATH.format(service_command_id)
        data, success = self._delete_method(api_path, "service command", logger)
        return success