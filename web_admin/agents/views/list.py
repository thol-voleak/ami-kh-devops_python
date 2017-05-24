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
    def get(self, request):
        context = {'agent_update_msg': self.request.session.pop('agent_update_msg', None)}
        return render(request, 'agents/list.html', context)

    def post(self, request, *args, **kwargs):
        # Get params
        unique_reference = request.POST.get('unique_reference', '')
        email = request.POST.get('email', '')
        primary_mobile_number = request.POST.get('primary_mobile_number', '')
        kyc_status = request.POST.get('kyc_status', '')
        from_created_timestamp = request.POST.get('from_created_timestamp', '')
        to_created_timestamp = request.POST.get('to_created_timestamp', '')

        context = {'unique_reference': unique_reference,
                   'email': email,
                   'primary_mobile_number': primary_mobile_number,
                   'kyc_status': kyc_status,
                   'from_created_timestamp': from_created_timestamp,
                   'to_created_timestamp': to_created_timestamp}

        # Build body
        body = {}
        if unique_reference is not '':
            body['unique_reference'] = unique_reference
        if email is not '':
            body['email'] = email
        if primary_mobile_number is not '':
            body['primary_mobile_number'] = primary_mobile_number
        if kyc_status is not '':
            if kyc_status.lower() == "true":
                kyc_status = True
            else:
                kyc_status = False
            body['kyc_status'] = kyc_status

        if from_created_timestamp is not '':
            from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            from_created_timestamp = from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = from_created_timestamp
        if to_created_timestamp is not '':
            to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            to_created_timestamp = to_created_timestamp.replace(hour=23, minute=59, second=59)
            to_created_timestamp = to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = to_created_timestamp

        api_path = SEARCH_AGENT

        data, status = self._post_method(
            api_path=api_path,
            func_description="Search Agent",
            logger=logger,
            params=body
        )
        context.update({'data': data})
        return render(request, 'agents/list.html', context)
