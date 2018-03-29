from web_admin.api_logger import API_Logger
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient, settings
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging

logger = logging.getLogger(__name__)


class EditView(TemplateView, RESTfulMethods):
    template_name = "shop-category/edit.html"
    raise_exception = False
    logger = logger
    login_url = 'web:permission_denied'

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        shop_category_id = kwargs['id']
        context = {}
        shop_category_detail = self.get_shop_category_detail(shop_category_id)
        context.update({
            'form': shop_category_detail['shop_categories'][0]
        })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update shop category ==========')
        shop_category_id = kwargs['id']
        form = request.POST
        params = {
            'name' : form['name'],
            'description' : form['description']
        }
        url = api_settings.EDIT_SHOP_CATEGORIES.format(shop_category_id=shop_category_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params)
        API_Logger.put_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            self.logger.info('========== Finish update shop category ==========')
            return redirect('shop_category:shop_category_list')
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)

    def get_shop_category_detail(self, shop_category_id):
        url = api_settings.GET_DETAIL_SHOP_CATEGORIES
        self.logger.info('========== Start get shop category detail ==========')
        body = {
            "id": shop_category_id
        }
        success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        if data is None:
            data = {}
            data['shop_categories'] = []

        API_Logger.post_logging(loggers=self.logger, params=body, response=data['shop_categories'],
                                status_code=status_code, is_getting_list=False)
        self.logger.info('========== Finish get shop category detail ==========')
        return data