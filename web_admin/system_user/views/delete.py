import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.contrib import messages

from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class DeleteView(TemplateView, RESTfulMethods):

    template_name = "delete.html"

    def get(self, request, *args, **kwargs):

        context = super(DeleteView, self).get_context_data(**kwargs)
        system_user_id = context['system_user_id']

        # LOAD DATA
        data = self._get_system_user_detail(system_user_id)

        context = {
            'system_user_info': data
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # Build API Path
        system_user_id = kwargs['system_user_id']
        api_path = settings.DELETE_SYSTEM_USER_URL.format(system_user_id)

        # Do Request
        data, status = self._delete_method(
            api_path=api_path,
            func_description="System User Delete",
            logger=logger
        )

        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
            return redirect('system_user:search')
        else:
            logger.info("Error deleting system user {}".format(system_user_id))

    def _get_system_user_detail(self, system_user_id):

        api_path = settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)

        data, status = self._get_method(
            api_path=api_path,
            func_description="System User Detail",
            logger=logger
        )

        return data
