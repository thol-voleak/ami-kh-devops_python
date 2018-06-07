from shop.utils import get_shop_details, convert_shop_to_form, convert_form_to_shop, get_all_shop_type, get_all_shop_category, get_agent_supported_channels, get_channel_permissions_list, get_devices_list, check_permission_device_management
from web_admin.api_logger import API_Logger
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient, ajax_functions
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
from django.urls import reverse
from web_admin.utils import get_back_url
import logging

logger = logging.getLogger(__name__)


class EditView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_EDIT_SHOP"
    template_name = "shop/edit.html"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

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

    def get(self, request, *args, **kwargs):
        shop_id = kwargs['id']
        context = {}
        shop = get_shop_details(self, shop_id)
        list_shop_type = get_all_shop_type(self)
        list_shop_category = get_all_shop_category(self)
        form = convert_shop_to_form(shop)

        permissions = check_permission_device_management(self)

        supported_channels = get_agent_supported_channels(self)
        access_channel_permissions = get_channel_permissions_list(self, shop_id)
        dict_channels = {int(x['id']): x for x in supported_channels}
        id_channels_permissions = {int(x['channel']['id']) for x in access_channel_permissions}
        for id, channel in dict_channels.items():
            if id in id_channels_permissions:
                channel['grant_permission'] = True
            else:
                channel['grant_permission'] = False

        device_list = get_devices_list(self, shop_id)
        supported_channels = dict_channels.values()
        context.update({
            'form': form,
            'list_shop_type': list_shop_type,
            'list_shop_category': list_shop_category,
            'supported_channels': supported_channels,
            'device_list': device_list,
            'permissions': permissions
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = request.POST
        shop_id = kwargs['id']
        shop = convert_form_to_shop(form)
        self.logger.info('========== Start update shop ==========')
        url = api_settings.EDIT_SHOP.format(shop_id=shop_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params=shop)
        if is_success:
            API_Logger.put_logging(loggers=self.logger, params=shop, response=data,
                               status_code=status_code)
            self.logger.info('========== Finish update shop ==========')
            messages.success(request, "Updated data successfully")
            return redirect(get_back_url(request, reverse('shop:shop_list')))
        else:
            context = {'form': form}
            messages.error(request, status_message)
            self.logger.info('========== Finish update shop ==========')
            return render(request, self.template_name, context)