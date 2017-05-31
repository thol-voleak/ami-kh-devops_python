import logging
from web_admin import api_settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class SystemUserUpdateForm(TemplateView, RESTfulMethods):

    template_name = "system_user/edit.html"

    def get(self, request, *args, **kwargs):
        logger.info("========== Start Updating system user ==========")
        logger.info("Start getting system user detail")
        context = super(SystemUserUpdateForm, self).get_context_data(**kwargs)
        system_user_id = context['systemUserId']

        # LOAD DATA
        data = self._get_system_user_detail(system_user_id)

        context = {
            'system_user_info': data,
            'msg': self.request.session.pop('system_user_update_msg', None)
        }
        logger.info("Finish getting system user detail")
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
        logger.info("========== Finish Updating system user ==========")
        if status:
            request.session['system_user_update_msg'] = 'Updated system user successfully'
            return redirect('system_user:system-user-detail', systemUserId=system_user_id)
        else:
            return render(request, self.template_name, context)

    def _get_system_user_detail(self, system_user_id):

        api_path = api_settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)

        data, status = self._get_method(
            api_path=api_path,
            func_description="System User Detail",
            logger=logger
        )

        return data

