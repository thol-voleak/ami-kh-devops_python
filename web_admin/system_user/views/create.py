import logging
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin import api_settings
from django.contrib import messages
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import encrypt_text
logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class SystemUserCreate(TemplateView, RESTfulMethods):

    template_name = "system_user/create.html"

    def get(self, request, *args, **kwargs):
        logger.info('========== Fetch form for creating new system user ==========')

        system_user_info = {
            "username": None,
            "firstname": None,
            "lastname": None,
            "email": None,
            "password": None,
        }

        context = {
            'system_user_info': system_user_info,
            'error_msg': None
        }

        logger.info('========== Finish fetching form for creating new system user ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        logger.info('========== Start creating new system user ==========')

        # Build API Path
        api_path = api_settings.SYSTEM_USER_CREATE_URL

        # Build params
        params = {
            "username": request.POST.get('username'),
            "firstname": request.POST.get('firstname'),
            "lastname": request.POST.get('lastname'),
            "email": request.POST.get('email'),
            "password": encrypt_text(request.POST.get('password')),
        }

        # Do Request
        data, status = self._post_method(
            api_path=api_path,
            func_description="System User Create",
            logger=logger,
            params=params
        )

        context = {
            'system_user_info': data
        }

        logger.info('========== Finish creating new system user ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Added data successfully')
            return redirect('system_user:system-user-list')
        else:
            context['error_msg'] = "Error occurred."
            return render(request, self.template_name, context)
