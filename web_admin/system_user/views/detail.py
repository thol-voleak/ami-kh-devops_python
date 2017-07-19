from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username
from .system_user_client import SystemUserClient

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "system_user/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting user detail ==========')
        context = super(DetailView, self).get_context_data(**kwargs)
        system_user_id = context['systemUserId']

        status_code, status_message, data = SystemUserClient.search_system_user(headers=self._get_headers(),
                                                                                logger=self.logger,
                                                                                user_id=system_user_id)
        context = {
            'system_user_info': data[0],
            'msg': self.request.session.pop('system_user_update_msg', None)
        }
        self.logger.info('========== Finish getting user detail ==========')
        return render(request, self.template_name, context)
