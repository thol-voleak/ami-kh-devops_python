import logging
from django.views.generic.base import TemplateView
from django.shortcuts import render
from web_admin.restful_methods import RESTfulMethods
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomerSOFListView(TemplateView, RESTfulMethods):
    template_name = 'member_customer_sof_list.html'

    def get(self, request, *args,**kwargs):
        logger.info('========== Start getting customer sof bank ==========')

        customer_id = int(kwargs.get('customerId'))

        url = settings.DOMAIN_NAMES + "report/v1/banks/sofs"
        logger.info('API-Path: {};'.format(url))
        param = {
            "user_id": customer_id
        }
        data, success = self._post_method(api_path=url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=param)

        context = {'data': data}
        logger.info('========== Finished searching customer sof ==========')
        return render(request, self.template_name, context)



