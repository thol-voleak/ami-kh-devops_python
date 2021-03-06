import logging

from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.contrib import messages
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import encrypt_text, setup_logger

logger = logging.getLogger(__name__)


class SystemUserCreate(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_CREATE_PERMISSION_ENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "system_user/create.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SystemUserCreate, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Fetch form for creating new system user ==========')

        system_user_info = {
            "username": None,
            "firstname": None,
            "lastname": None,
            "mobile_number": None,
            "email": None,
            "password": None,
        }

        context = {
            'system_user_info': system_user_info,
        }

        self.logger.info('========== Finish fetching form for creating new system user ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating new system user ==========')

        # Build API Path
        api_path = api_settings.CREATE_SYSTEM_USER_URL

        # Build params
        params = {
            "username": request.POST.get('username'),
            "firstname": request.POST.get('firstname'),
            "lastname": request.POST.get('lastname'),
            "mobile_number": request.POST.get('mobile_number'),
            "email": request.POST.get('email'),
            "password": encrypt_text(request.POST.get('password')),
        }

        # Do Request
        data, status = self._post_method(
            api_path=api_path,
            func_description="System User Create",
            params=params
        )

        context = {
            'system_user_info': data
        }

        self.logger.info('========== Finish creating new system user ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Added data successfully')
            return redirect('system_user:system-user-list')
        else:
            context = {
                'system_user_info': params,
                'user_error_msg': data
            }
            # context['user_error_msg'] = data
            return render(request, self.template_name, context)
