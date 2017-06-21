import logging
from web_admin import api_settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
logger = logging.getLogger(__name__)


class DeleteCommand(View, RESTfulMethods):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DeleteCommand, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        service_command_id = kwargs.get('service_command_id')
        self.logger.info('========== Start deleting Service Command ==========')
        success = self._delete_service_command(service_command_id)
        self.logger.info('========== Finish deleting Service Command ==========')

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()


    def _delete_service_command(self, service_command_id):
        api_path = api_settings.SERVICE_COMMAND_DELETE_PATH.format(service_command_id)
        data, success = self._delete_method(api_path, "service command", logger)
        return success