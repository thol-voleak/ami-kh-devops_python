from authentications.utils import get_correlation_id_from_username
from web_admin.api_settings import SEARCH_CARD_TYPE, UPDATE_CARD_TYPE
from web_admin.restful_client import RestFulClient
from web_admin import setup_logger
from django.http import HttpResponseRedirect
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class CardTypeUpdateForm(GetHeaderMixin, TemplateView):
    template_name = "card_type/card_type_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardTypeUpdateForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Card Type update page ==========')
        context = super(CardTypeUpdateForm, self).get_context_data(**kwargs)
        card_type_id = context['cardTypeId']
        data = self._get_card_type_detail(card_type_id)
        result = {
            'card_type': data
        }
        self.logger.info('========== Finished showing Card Type update page ==========')
        return result

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating Card type ==========')

        card_type_id = kwargs['cardTypeId']
        card_type_name = request.POST.get('card_type_name_input')
        timeout_create_card = request.POST.get('timeout_create_card_input')
        timeout_get_card_detail = request.POST.get('timeout_get_card_detail_input')
        url_create_card = request.POST.get('url_create_card_input')
        url_get_card_detail = request.POST.get('url_get_card_detail_input')
        url_update_card_status = request.POST.get('url_update_card_status')
        timeout_update_card_status = request.POST.get('timeout_update_card_status')

        timeout_create_card_in_millisecond = int(timeout_create_card) * 1000
        timeout_get_card_detail_in_millisecond = int(timeout_get_card_detail) * 1000
        try :
            timeout_update_card_status = int(timeout_update_card_status) * 1000
        except Exception as e:
            timeout_update_card_status = ''

        params = {
            'name': card_type_name,
            'timeout_create_card': timeout_create_card_in_millisecond,
            'timeout_get_card_detail': timeout_get_card_detail_in_millisecond,
            'create_card_endpoint_host': url_create_card,
            'card_detail_endpoint_host': url_get_card_detail,
            'update_card_status_endpoint_host': url_update_card_status,
            'timeout_update_card_status': timeout_update_card_status
        }

        is_success, status_code, status_message, data = RestFulClient.put(url=UPDATE_CARD_TYPE.format(card_type_id=card_type_id), headers=self._get_headers(), params=params, loggers=self.logger, timeout=settings.GLOBAL_TIMEOUT)
        if is_success:
            previous_page = request.POST.get('previous_page')
            request.session['card_type_update_msg'] = 'Updated card type successfully'
            self.logger.info('========== Finished updating Card type ==========')
            return redirect('card_type:card-type-list')
        self.logger.info('========== Finished updating Card type ==========')
        return redirect(request.META['HTTP_REFERER'])

    def _get_card_type_detail(self, card_type_id):
        is_success, status_code, status_message, data = RestFulClient.post(url=SEARCH_CARD_TYPE, headers=self._get_headers(), params={'id': card_type_id}, loggers=self.logger, timeout=settings.GLOBAL_TIMEOUT)
        timeout_create_card_in_second = int(data[0]['timeout_create_card']) / 1000
        timeout_get_card_detail_in_second = int(data[0]['timeout_get_card_detail']) / 1000
        try:
            result = int(data[0]['timeout_update_card_status']) / 1000
        except Exception as e:
            timeout_update_card_status_in_second = ''
        else:
            timeout_update_card_status_in_second = result
    
        # timeout_update_card_status_in_second = int(data[0]['timeout_update_card_status']) / 1000
        data[0].update({'timeout_create_card_in_second': '%g' % timeout_create_card_in_second,
                        'timeout_get_card_detail_in_second': '%g' % timeout_get_card_detail_in_second,
                        'timeout_update_card_status_in_second': '%s' % timeout_update_card_status_in_second})
        return data[0]
