import requests
import logging
import time

from django.views.generic.base import TemplateView
from django.shortcuts import render

from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

class ListView(TemplateView, RESTfulMethods):
    template_name = 'member_customer_list.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        logger.info('========== Start getting Customer List ==========')
        customer_list = self.get_member_customer_list()
        logger.info('========== Finished getting Customer List ==========')
        context['data'] = customer_list
        context['search_count'] = len(customer_list)
        return context

    def get_member_customer_list(self):
        url = api_settings.MEMBER_CUSTOMER_PATH
        data, success = self._post_method(api_path= url,
                                          func_description="member customers list",
                                          logger=logger,
                                          params={})
        return data

    def post(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        logger.info('========== Start searching Customer ==========')
        url = api_settings.MEMBER_CUSTOMER_PATH
        search = request.POST.get('search')
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
        logger.info('========== Finished searching Customer ==========')
        return render(request, 'member_customer_list.html', context)

