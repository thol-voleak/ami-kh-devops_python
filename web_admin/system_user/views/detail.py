import logging
from web_admin import api_settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class DetailView(TemplateView, RESTfulMethods):

    template_name = "system_user/detail.html"

    def get(self, request, *args, **kwargs):

        context = super(DetailView, self).get_context_data(**kwargs)
        system_user_id = context['systemUserId']

        # LOAD DATA
        data = self._get_system_user_detail(system_user_id)

        context = {
            'system_user_info': data,
            'msg': self.request.session.pop('system_user_update_msg', None)
        }

        return render(request, self.template_name, context)

    def _get_system_user_detail(self, system_user_id):

        api_path = api_settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)

        data, status = self._get_method(
            api_path=api_path,
            func_description="System User Detail",
            logger=logger
        )

        return data
