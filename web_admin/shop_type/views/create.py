from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.shortcuts import render, redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView, GetHeaderMixin):

    template_name = "shop-type/create.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        self.logger.info('========== User go to Add New Shop Type page ==========')
        return render(request, self.template_name, context)

    def post(self, request):
        self.logger.info('========== Start Adding new shop type ==========')
        form = request.POST
        params = {
            'name': form['name'],
            'description': form['description']
        }
        success, status_code, message, data = self.add_shop_type(params)
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added data successfully'
            )
        self.logger.info('========== Finish Adding new shop type ==========')
        return redirect('shop_type:shop_type_list')

    def add_shop_type(self, params):
        success, status_code, message, data = RestFulClient.post(
            url=api_settings.SHOP_TYPE_CREATE,
            params=params, loggers=self.logger,
            headers=self._get_headers()
        )
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                               status_code=status_code)
        return success, status_code, message, data
