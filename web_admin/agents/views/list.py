import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

STATUS = {
    1: 'Active',
}

KYC = {
    True: 'YES',
    False: 'NO',
}

class ListView(TemplateView, RESTfulMethods):
    template_name = 'agents/list.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        data = self.get_agent_list()
        context.update({'data': self.format_data(data)})
        context.update({'agent_update_msg': self.request.session.pop(
            'agent_update_msg', None)})
        return context

    def get_agent_list(self):
        data, success = self._get_method(api_path=settings.AGENT_LIST_PATH,
                                         func_description="Agent List",
                                         logger=logger,
                                         is_getting_list=True)
        return data


    def format_data(self, data):
        for i in data:
            i['kyc_status'] = KYC.get(i.get('kyc_status'))
            i['status'] = STATUS.get(i.get('status'))
        return data