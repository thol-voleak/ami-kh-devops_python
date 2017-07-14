import logging
from django.views.generic.base import TemplateView
from django.shortcuts import render
from web_admin.restful_methods import RESTfulMethods
from django.conf import settings
from web_admin.utils import setup_logger
logger = logging.getLogger(__name__)


class CustomerSOFListView(TemplateView, RESTfulMethods):
    template_name = 'member_customer_sof_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(CustomerSOFListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args,**kwargs):
        self.logger.info('========== Start getting customer sof bank ==========')

        customer_id = int(kwargs.get('customerId'))

        url = settings.DOMAIN_NAMES + "report/v1/banks/sofs"
        self.logger.info('API-Path: {};'.format(url))
        param = {
            "user_id": customer_id
        }
        data, success = self._post_method(api_path=url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=param)

        context = {'data': data}
        self.logger.info('========== Finished searching customer sof ==========')
        return render(request, self.template_name, context)



