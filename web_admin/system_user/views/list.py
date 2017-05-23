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
class ListView(TemplateView, RESTfulMethods):

    template_name = "list.html"

    def get(self, request, *args, **kwargs):

        # LOAD DATA
        data = self._get_system_user_list()

        context = {
            'data': data,
            'created_msg': self.request.session.pop('system_user_create_msg', None),
            'del_msg': self.request.session.pop('system_user_delete_msg', None),
            'pw_msg': self.request.session.pop('system_user_change_password_msg', None)
        }

        return render(request, self.template_name, context)

    def _get_system_user_list(self):
        api_path = api_settings.GET_ALL_SYSTEM_USER

        data, status = self._get_method(
            api_path=api_path,
            func_description="System User List",
            logger=logger,
            is_getting_list=True
        )

        return data
