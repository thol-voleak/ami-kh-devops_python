import logging
from django.views.generic.base import TemplateView
from django.shortcuts import render
from web_admin.restful_methods import RESTfulMethods
from django.conf import settings
from web_admin.utils import setup_logger
from web_admin.api_settings import CUSTOMER_IDENTITIES_LIST
logger = logging.getLogger(__name__)


class CustomerIdentitiesListView(TemplateView, RESTfulMethods):
    template_name = 'member_customer_identities.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(CustomerIdentitiesListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args,**kwargs):
        self.logger.info('========== Start getting member customer identities ==========')
        customer_id = int(kwargs.get('customerId'))
        url = CUSTOMER_IDENTITIES_LIST
        self.logger.info('API-Path: {};'.format(url))
        param = {}
        data, success = self._get_method(api_path=url,
                                          func_description="member customer identities",
                                          logger=logger,
                                          params=param)

        context = {'customer_id':customer_id,'data': data}
        self.logger.info('========== Finished member customer identities ==========')
        return render(request, self.template_name, context)



