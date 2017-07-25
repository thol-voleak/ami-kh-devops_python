from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, get_auth_header, check_permissions_by_user
from authentications.apps import InvalidAccessToken
from web_admin import setup_logger
from .system_user_client import SystemUserClient

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView):
    group_required = "SYS_MANAGE_SYSTEM_USER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "system_user/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'data': [],
            'created_msg': self.request.session.pop('system_user_create_msg', None),
            'del_msg': self.request.session.pop('system_user_delete_msg', None),
            'pw_msg': self.request.session.pop('system_user_change_password_msg', None)
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info("========== Start searching system user ==========")
        username = request.POST.get('username')
        email = request.POST.get('email')
        params = {}
        if username:
            params['username'] = username
        if email:
            params['email'] = email

        status_code, status_message, data = SystemUserClient.search_system_user(self._get_headers(),
                                                                                self.logger, username, email, None)
        if (status_code == "access_token_expire") or \
                (status_code == 'authentication_fail') or \
                (status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)

        is_permission_detail = check_permissions_by_user(self.request.user, 'SYS_VIEW_SYSTEM_USER')
        is_permission_edit = check_permissions_by_user(self.request.user, 'SYS_EDIT_SYSTEM_USER')
        is_permission_delete = check_permissions_by_user(self.request.user, 'SYS_DELETE_SYSTEM_USER')
        is_permission_change_pwd = check_permissions_by_user(self.request.user, 'SYS_CHANGE_SYSTEM_USER_PASSWORD')
        is_permission_change_role = check_permissions_by_user(self.request.user, 'CAN_CHANGE_ROLE_FOR_USER')

        for i in data:
            i['is_permission_detail'] = is_permission_detail
            i['is_permission_edit'] = is_permission_edit
            i['is_permission_delete'] = is_permission_delete
            i['is_permission_change_pwd'] = is_permission_change_pwd
            i['is_permission_change_role'] = is_permission_change_role

        context['data'] = data
        context['username'] = username
        context['email'] = email
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
