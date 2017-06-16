import logging

from datetime import datetime
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from django.shortcuts import render
from web_admin.api_settings import SEARCH_AGENT

logger = logging.getLogger(__name__)

STATUS = {
    1: 'Active',
}

class ListView(TemplateView, RESTfulMethods):

    template_name = 'agents/list.html'

    def get(self, request, *args, **kwargs):
        logger.info('========== Start showing Agent List page ==========')
        context = {
            'agent_update_msg': self.request.session.pop('agent_update_msg', None)
        }

        # Set first load default time for Context
        from_created_timestamp = datetime.now()
        from_created_timestamp = from_created_timestamp.replace(hour=0, minute=0, second=1)
        new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        to_created_timestamp = datetime.now()
        to_created_timestamp = to_created_timestamp.replace(hour=23, minute=59, second=59)
        new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build Body
        body = {}

        context.update(body)
        body['from_created_timestamp'] = new_from_created_timestamp
        new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%d")
        context['from_created_timestamp'] = new_from_created_timestamp

        body['to_created_timestamp'] = new_to_created_timestamp
        new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%d")
        context['to_created_timestamp'] = new_to_created_timestamp

        # Get Data
        data = self._get_agents(params=body)
        context['data'] = data

        logger.info('========== Finished showing Agent List page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # Get params
        unique_reference = request.POST.get('unique_reference')
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        kyc_status = request.POST.get('kyc_status')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        # Build Body
        context = {}
        body = {}
        if unique_reference:
            body['unique_reference'] = unique_reference
        if email:
            body['email'] = email
        if primary_mobile_number:
            body['primary_mobile_number'] = primary_mobile_number

        if kyc_status and isinstance(kyc_status, str):
            if kyc_status.lower() == "true":
                new_kyc_status = True
            else:
                new_kyc_status = False
            body['kyc_status'] = new_kyc_status
            context['kyc_status'] = kyc_status

        context.update(body)

        if from_created_timestamp is not '':
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp
            context['from_created_timestamp'] = from_created_timestamp

        if to_created_timestamp is not '':
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp
            context['to_created_timestamp'] = to_created_timestamp

        # Get Data
        data = self._get_agents(params=body)
        context['data'] = data

        return render(request, self.template_name, context)

    def _get_agents(self, params):
        logger.info('========== Start searching agent ==========')

        api_path = SEARCH_AGENT
        data, status = self._post_method(
            api_path=api_path,
            func_description="Search Agent",
            logger=logger,
            params=params
        )

        logger.info('========== Finished searching agent ==========')
        return data