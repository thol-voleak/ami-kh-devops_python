import logging

import requests
from multiprocessing.pool import ThreadPool
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import format_date_time

logger = logging.getLogger(__name__)


class CommissionAndPaymentView(TemplateView, GetHeaderMixin):
    template_name = "services/commission_and_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(CommissionAndPaymentView, self).get_context_data(*args, **kwargs)
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        logger.info('Get CommissionAndPaymentView by user: {}'.format(
            self.request.user.username
        ))

        logger.info('========== Start get commission and payment list ==========')
        data, success = self._get_commission_and_payment_list(tier_id)
        logger.info('========== Finish get commission and payment list ==========')

        logger.info('========== Start get setting bonus list ==========')
        bonus, success = self._get_setting_bonus_list(tier_id)
        logger.info('========== Finish get setting bonus list ==========')

        choices = self._get_choices()

        context['data'] = data
        context['choices'] = choices
        context['bonus'] = bonus
        return context

    def _get_choices(self):
        url_list = [settings.ACTION_TYPES_URL, settings.AMOUNT_TYPES_URL,
                    settings.SOF_TYPES_URL, settings.ACTOR_TYPES_URL]
        pool = ThreadPool(processes=1)

        async_list = map(lambda url: pool.apply_async(lambda: self._get_choices_types(url)),
                         url_list)
        result_list = list(map(lambda x: x.get(), async_list))
        return {
            'action_types': result_list[0],
            'amount_types': result_list[1],
            'sof_types': result_list[2],
            'actor_types': result_list[3],
        }

    def _get_choices_types(self, url):
        logger.info("Get choices for table from url: {}".format(url))
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        json_data = response.json()
        logger.info("Reponse status code: {}".format(response.status_code))
        return json_data['data']

    def _get_commission_and_payment_list(self, fee_tier_id):
        url = settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        json_data = response.json()
        logger.info("Response status: {}".format(response.status_code))
        if response.status_code == 200:
            data = json_data.get('data', [])
            logger.info("Commission and payment list count: {}".format(len(data)))
            data = format_date_time(data)
            return data, True
        else:
            logger.info("Response content: {}".format(response.content))
        return [], False

    def _get_setting_bonus_list(self, fee_tier_id):
        url = settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        json_data = response.json()
        logger.info("Response status: {}".format(response.status_code))
        if response.status_code == 200:
            data = json_data.get('data', [])
            logger.info("Setting Bonus list count: {}".format(len(data)))
            data = format_date_time(data)
            return data, True
        else:
            logger.info("Response content: {}".format(response.content))
        return [], False


class PaymentAndFeeStructureView(TemplateView, GetHeaderMixin):

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.TIER_DETAIL_URL.format(fee_tier_id=fee_tier_id)

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
        }
        response = requests.post(url, headers=self._get_headers(),
                                 json=post_data, verify=settings.CERT)

        logger.info("Response status: {}".format(response.status_code))
        if response.status_code == 200:
            messages.add_message(
                request,
                messages.INFO,
                'Adding success!'
            )
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
            logger.info("Response content: {}".format(response.content))
        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)


class SettingBonusView(TemplateView, GetHeaderMixin):

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
        }
        response = requests.post(url, headers=self._get_headers(),
                                 json=post_data, verify=settings.CERT)

        logger.info("Response status: {}".format(response.status_code))
        if response.status_code == 200:
            messages.add_message(
                request,
                messages.INFO,
                'Added setting bonus successfully'
            )
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
            logger.info("Response content: {}".format(response.content))
        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)
