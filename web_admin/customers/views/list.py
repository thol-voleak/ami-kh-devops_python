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

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        logger.info('========== Start searching Customer ==========')
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
        logger.info('========== Finished searching Customer ==========')
        return render(request, 'member_customer_list.html', context)

