from braces.views import GroupRequiredMixin
from web_admin.restful_methods import RESTfulMethods
from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import GET_PAYMENT_DETAIL
from django.contrib import messages
from authentications.apps import InvalidAccessToken
from authentications.utils import check_permissions_by_user, get_correlation_id_from_username

logger = logging.getLogger(__name__)

STATUS_ORDER = {
    -1: 'FAIL',
     0: 'CREATED',
     1: 'LOCKING',
     2: 'EXECUTED',
     3: 'ROLLED_BACK',
     4: 'TIME_OUT',
}

IS_DELETED = {
    True: 'Yes',
    False: 'No',
}

SOF_TYPE = {
    1: 'Bank',
    2: 'Cash',
    3: 'Card'
}

class OrderDetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "payments/order_detail.html"
    logger = logger

    group_required = "CAN_VIEW_PAYMENT_ORDER_DETAIL"
    login_url = 'web:permission_denied'
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(OrderDetailView, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting order detail ==========')
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order_id = context['order_id']
        url  = GET_PAYMENT_DETAIL.format(order_id=order_id)
        is_success, status_code, data = RestFulClient.get(url, loggers=self.logger, headers=self._get_headers())
        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
            messages.add_message(
                self.request,
                messages.ERROR,
                "Something went wrong"
            )
        if data:
            data['status'] = STATUS_ORDER.get(data['status'], 'UN_KNOWN')
            data['is_deleted'] = IS_DELETED.get(data.get('is_deleted'))
            data['initiator_user']['sof_type_id'] = SOF_TYPE.get(data['initiator_user']['sof_type_id'])
            data['payer_user']['sof_type_id'] = SOF_TYPE.get(data['payer_user']['sof_type_id'])
            data['payee_user']['sof_type_id'] = SOF_TYPE.get(data['payee_user']['sof_type_id'])
        context['data'] = data
        self.logger.info('Response_content: {}'.format(data))
        self.logger.info('========== End getting order detail ==========')
        return render(request, self.template_name, context)
