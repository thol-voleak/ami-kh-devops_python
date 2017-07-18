from authentications.utils import get_correlation_id_from_username
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView
from django.shortcuts import render

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = 'member_customer_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info('========== Start searching Customer ==========')
        url = api_settings.MEMBER_CUSTOMER_PATH
        search = request.GET.get('search')
        if search is None:
            data = {}
        else:
            if search == '':
                params = {}
            else:
                params = {"mobile_number": search}
            data, success = self._post_method(api_path= url,
                                              func_description="search member customer",
                                              logger=logger,
                                              params=params)
        context['search_count'] = len(data)
        context['data'] = data
        self.logger.info('========== Finished searching Customer ==========')
        return render(request, 'member_customer_list.html', context)

