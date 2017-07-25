from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from braces.views import GroupRequiredMixin

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleDeleteView(GroupRequiredMixin, TemplateView):
    template_name = "roles/delete.html"
    logger = logger

    group_required = "CAN_DELETE_ROLE"
    login_url = 'authentications:login'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RoleDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get role entity ==========')
        context = super(RoleDeleteView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        self.logger.info("Searching role with [{}] role id".format(role_id))
        params = {
            'id': role_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params)
        if is_success:
            context['role'] = data[0]
            self.logger.info('========== End get role entity ==========')

        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start delete role entity ==========')
        role_id = kwargs['role_id']
        url = api_settings.ROLE_DELETE_PATH.format(role_id=role_id)

        is_success, status_code, status_message = RestFulClient.delete(url=url,
                                                                       headers=self._get_headers(),
                                                                       loggers=self.logger)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted role entity successfully'
            )
            self.logger.info('========== End delete role entity ==========')
            return redirect('authentications:role_list')
        elif (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                    status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                status_message
            )
            self.logger.info('========== End delete role entity ==========')
            return redirect('authentications:delete_role', role_id=role_id)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
