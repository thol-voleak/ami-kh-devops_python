from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header
from web_admin.utils import format_date_time

import requests
import logging

logger = logging.getLogger(__name__)


class ListCommandView(TemplateView):
    template_name = "command/list.html"

    def get_context_data(self, **kwargs):
        context = super(ListCommandView, self).get_context_data(**kwargs)
        service_id = context['service_id']
        logger.info('========== Start get Command List ==========')
        data, service_name = self.get_commands_list(service_id)
        refined_data = format_date_time(data)
        logger.info('========== Finished get Command List ==========')
        context['data'] = refined_data
        context['service_name'] = service_name
        return context

    def get_commands_list(self, service_id):
        logger.info("Getting command list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)

        url = settings.COMMAND_LIST_BY_SERVICE_URL.format(service_id)

        logger.info("Getting command list from backend with {} url".format(url))
        auth_request = requests.get(url, headers=headers, verify=settings.CERT)

        json_data = auth_request.json()

        detail_url = settings.SERVICE_DETAIL_URL.format(service_id)
        service_detail = requests.get(detail_url, headers=headers, verify=settings.CERT)
        service_detail = service_detail.json().get("data")
        data = json_data.get('data')
        service_name = service_detail["service_name"]

        if auth_request.status_code == 200:
            if data is not None:
                logger.info('Service count: {}'.format(len(data)))
                return data, service_name

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))
