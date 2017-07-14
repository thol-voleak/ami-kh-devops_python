import logging
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from .system_user_client import SystemUserClient
logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class DetailView(TemplateView, RESTfulMethods):

    template_name = "system_user/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting user detail ==========')
        context = super(DetailView, self).get_context_data(**kwargs)
        system_user_id = context['systemUserId']

        status_code, status_message, data = SystemUserClient.search_system_user(self.request, self._get_headers(), logger, None, None, system_user_id)

        context = {
            'system_user_info': data[0],
            'msg': self.request.session.pop('system_user_update_msg', None)
        }
        self.logger.info('========== Finish getting user detail ==========')
        return render(request, self.template_name, context)
