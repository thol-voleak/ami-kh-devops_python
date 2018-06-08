from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_shop_details, convert_shop_to_form
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.conf import settings
from braces.views import GroupRequiredMixin
from django.contrib import messages

from shop.utils import check_permission_device_management, get_agent_supported_channels, \
    get_channel_permissions_list, get_devices_list

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_VIEW_SHOP"
    template_name = "shop/detail.html"
    raise_exception = False
    logger = logger
    login_url = 'web:permission_denied'

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        permissions = {}
        permissions['CAN_EDIT_SHOP'] = self.check_membership(["CAN_EDIT_SHOP"])
        shop_id = int(kwargs['id'])
        shop = get_shop_details(self, shop_id)
        form = convert_shop_to_form(shop)

        permissions.update(check_permission_device_management(self))

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

        context = {
            'form': form,
            'permissions':permissions,
            'supported_channels': supported_channels,
            'device_list': device_list,
        }
        return render(request, self.template_name, context)
