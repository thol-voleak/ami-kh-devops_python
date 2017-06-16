import logging
from web_admin import api_settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)


class DeleteCommand(View, RESTfulMethods):
    def delete(self, request, *args, **kwargs):
        service_command_id = kwargs.get('service_command_id')
        logger.info('========== Start deleting Service Command ==========')
        success = self._delete_service_command(service_command_id)
        logger.info('========== Finish deleting Service Command ==========')

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()


    def _delete_service_command(self, service_command_id):
        api_path = api_settings.SERVICE_COMMAND_DELETE_PATH.format(service_command_id)
        data, success = self._delete_method(api_path, "service command", logger)
        return success