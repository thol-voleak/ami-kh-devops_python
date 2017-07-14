import logging
from web_admin import api_settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from .system_user_client import SystemUserClient
logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class SystemUserUpdateForm(TemplateView, RESTfulMethods):

    template_name = "system_user/update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SystemUserUpdateForm, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info("========== Start Updating system user ==========")
        self.logger.info("Start getting system user detail")
        context = super(SystemUserUpdateForm, self).get_context_data(**kwargs)
        system_user_id = context['systemUserId']

        status_code, status_message, data = SystemUserClient.search_system_user(self.request, self._get_headers(), logger, None, None, system_user_id)

        context = {
            'system_user_info': data[0],
            'msg': self.request.session.pop('system_user_update_msg', None)
        }
        self.logger.info("Finish getting system user detail")
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # Build API Path
        system_user_id = kwargs['systemUserId']
        api_path = api_settings.UPDATE_SYSTEM_USER_URL.format(system_user_id)

        # Build params
        username = request.POST.get('username_input')
        firstname = request.POST.get('firstname_input')
        lastname = request.POST.get('lastname_input')
        email = request.POST.get('email_input')

        params = {
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "email": email
        }

        # Do Request
        data, status = self._put_method(
            api_path=api_path,
            func_description="System User Update",
            logger=logger,
            params=params
        )

        context = {
            'system_user_info': data
        }
        self.logger.info("========== Finish Updating system user ==========")
        if status:
            request.session['system_user_update_msg'] = 'Updated system user successfully'
            return redirect('system_user:system-user-detail', systemUserId=system_user_id)
        else:
            params['id'] = system_user_id
            context = {
                'system_user_info': params,
                'msg': data
            }
            return render(request, self.template_name, context)
