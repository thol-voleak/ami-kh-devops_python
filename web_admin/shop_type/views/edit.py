from web_admin.api_logger import API_Logger
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging

logger = logging.getLogger(__name__)


class EditView(GroupRequiredMixin, TemplateView):
    template_name = "shop-type/edit.html"
    raise_exception = False
    logger = logger
    # group_required = "CAN_EDIT_PRODUCT"
    login_url = 'web:permission_denied'

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    # def check_membership(self, permission):
    #     self.logger.info(
    #         "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
    #     return check_permissions_by_user(self.request.user, permission[0])

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get shop type detail ==========')
        context = super(EditView, self).get_context_data(**kwargs)
        shop_type_id = context['shop_type_id']
        self.logger.info("Searching shop type with [{}] shop type id".format(shop_type_id))
        params = {
            'id': shop_type_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_LIST_SHOP_TYPE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params)
        if is_success:
            context['form'] = data['shop_types'][0]
            self.logger.info('========== Finish get shop type detail ==========')
            return context
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)


    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update shop type ==========')
        shop_type_id = kwargs['shop_type_id']
        form = request.POST
        params = {
            'name' : form['name'],
            'description' : form['description']
        }
        url = api_settings.EDIT_SHOP_TYPE.format(shop_type_id=shop_type_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            self.logger.info('========== Finish update shop type ==========')
            return redirect('shop_type:shop_type_list')
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
