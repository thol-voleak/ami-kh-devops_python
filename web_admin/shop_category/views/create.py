from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging
from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)


class CreateView(TemplateView):
    template_name = "shop-category/create.html"
    # group_required = "CAN_ADD_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    # def get(self, request, *args, **kwargs):
    #     context = super(CreateView, self).get_context_data(**kwargs)
    #     return render(request, self.template_name, context)

    # def check_membership(self, permission):
    #     self.logger.info(
    #         "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
    #     return check_permissions_by_user(self.request.user, permission[0])

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start Adding new shop category ==========')
        form = request.POST
        params = {
            'name': form['name'],
            'description': form['description']
        }
        success, status_code, message, data = RestFulClient.post(
            url=api_settings.CREATE_SHOP_CATEGORY,
            params=params, loggers=self.logger,
            headers=self._get_headers()
        )
        self.logger.info("Params: {} ".format(params))
        if success:
            self.logger.info('========== Finish Adding new shop category ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added data successfully'
            )
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        
        
        return redirect('shop_category:shop_category_list')