import logging
import time
import requests

from multiprocessing.pool import ThreadPool
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from authentications.utils import get_auth_header
from web_admin.get_header_mixins import GetHeaderMixin
from .mixins import GetCommandNameAndServiceNameMixin
from authentications.apps import InvalidAccessToken
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class CommissionAndPaymentView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission_and_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(CommissionAndPaymentView, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

        fee_tier_detail, success = self._get_fee_tier_detail(tier_id)

        data, success = self._get_commission_and_payment_list(tier_id)

        bonus, success = self._get_setting_bonus_list(tier_id)

        agent_bonus_distribution, success = self._get_agent_bonus_distribution_list(tier_id)
        total_bonus_distribution = self._filter_deleted_items(agent_bonus_distribution)

        fee, success = self._get_agent_fee_distribution_list(tier_id)
        choices = self._get_choices()

        context['fee_tier_detail'] = fee_tier_detail
        context['data'] = self._filter_deleted_items(data)
        context['bonus'] = self._filter_deleted_items(bonus)
        context['agent_bonus_distribution'] = total_bonus_distribution
        context['fee'] = self._filter_deleted_items(fee)
        context['choices'] = choices
        logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        logger.info('========== Finish get command name ==========')

        logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        logger.info('========== Finish get service name ==========')
        return context

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

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
        api_path = settings.DOMAIN_NAMES + url
        response = requests.get(api_path, headers=self._get_headers(), verify=settings.CERT)
        json_data = response.json()
        logger.info("Reponse status code: {}".format(response.status_code))
        return json_data['data']

    def _get_fee_tier_detail(self, fee_tier_id):
        # api_path, header, verify, func_description, logger, is_getting_list = False, params = {}
        data, success = self._get_method(api_path=settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment & Fee Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(api_path=settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
                                         func_description="Agent bonus distribution",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(api_path=settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Agent Fee Distribution List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

class PaymentAndFeeStructureView(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):

        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.DOMAIN_NAMES + settings.TIER_DETAIL_URL.format(fee_tier_id=fee_tier_id)

        logger.info('========== Start create Setting Payment & Fee Structure ==========')
        logger.info('Create Payment and Fee Structure by user: {}, with url {}.'.format(
            self.request.user.username,
            url,
        ))

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }

        logger.info("Request body: {}".format(post_data))
        response = requests.post(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)

        logger.info("Response status: {}".format(response.status_code))
        logger.info("Response content: {}".format(response.content))
        if response.status_code == 200:
            messages.add_message(
                request,
                messages.INFO,
                'Added data successfully'
            )
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
        logger.info('========== Finish create Setting Payment & Fee Structure ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)


class BalanceDistributionsUpdate(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        logger.info("========== Start updating setting payment & fee structure ==========")

        balance_distribution_id = kwargs.get('balance_distributions_id')
        api_path = settings.BALANCE_DISTRIBUTION_UPDATE_URL.format(balance_distribution_id=balance_distribution_id)
        url = settings.DOMAIN_NAMES + api_path
        logger.info("API-Path: {}".format(api_path))

        data = request.POST.copy()
        post_data = {
            "fee_tier_id": data.get("fee_tier_id"),
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "specific_actor_id": data.get("specific_actor_id"),
            "sof_type_id": data.get('sof_type_id'),
            "specific_sof": data.get("specific_sof"),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            # "specific_actor_id": data.get("specific_actor_id"),
        }
        logger.info("Params: {}".format(post_data))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        end_date = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_date - start_date))

        if response.status_code == 200:
            httpResponse = HttpResponse(status=200, content=response)
        else:
            httpResponse = HttpResponse(status=response.status_code, content=response)

        logger.info("========== Finished updating setting payment & fee structure ==========")
        return httpResponse


class BonusDistributionsUpdate(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        logger.info("========== Start update setting bonus ==========")

        bonus_distributions_id = kwargs.get('bonus_distributions_id')

        api_path = settings.BONUS_DISTRIBUTION_UPDATE_URL.format(bonus_distributions_id=bonus_distributions_id)
        url = settings.DOMAIN_NAMES + api_path
        logger.info("API-Path: {}".format(api_path))

        data = request.POST.copy()

        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get('sof_type_id'),
            "specific_sof": data.get("specific_sof"),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }
        logger.info("Params: {}".format(post_data))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        end_date = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_date - start_date))

        if response.status_code == 200:
            httpResponse = HttpResponse(status=200, content=response)
        else:
            httpResponse = HttpResponse(status=response.status_code, content=response)

        logger.info("========== Finish update setting bonus ==========")
        return httpResponse

class AgentBonusDistributionsUpdate(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        logger.info("========== Start updating agent bonus distribution ==========")

        agent_bonus_distribution_id = kwargs.get('agent_bonus_distribution_id')
        api_path = settings.AGENT_BONUS_DISTRIBUTION_UPDATE_URL.format(agent_bonus_distribution_id=agent_bonus_distribution_id)
        url = settings.DOMAIN_NAMES + api_path
        logger.info("API-Path: {}".format(api_path))

        data = request.POST.copy()
        post_data = {
            "fee_tier_id": data.get("fee_tier_id"),
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get('sof_type_id'),
            "specific_sof": data.get("specific_sof"),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }
        logger.info("Params: {}".format(post_data))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        end_date = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_date - start_date))

        if response.status_code == 200:
            httpResponse = HttpResponse(status=200, content=response)
        else:
            httpResponse = HttpResponse(status=response.status_code, content=response)

        logger.info("========== Finished updating agent bonus distribution ==========")
        
        return httpResponse

class SettingBonusView(TemplateView, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.DOMAIN_NAMES + settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        logger.info('========== Start create Setting Bonus ==========')
        logger.info('Username: {}, with url {}.'.format(self.request.user.username, url))

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }

        logger.info("Request: {}".format(post_data))
        response = requests.post(url, headers=self._get_headers(),
                                 json=post_data, verify=settings.CERT)

        logger.info("Response status: {}".format(response.status_code))
        logger.info("Response content: {}".format(response.content))
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

        logger.info('========== Finish create Setting Bonus ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)

class PaymentAndFeeStructureDetailView(View, RESTfulMethods):
    def delete(self, request, *args, **kwargs):
        balance_distribution_id = kwargs.get('balance_distribution_id')

        success = self._delete_balance_distribution(balance_distribution_id)

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_balance_distribution(self, balance_distribution_id):
        data, success = self._delete_method(api_path=settings.BALANCE_DISTRIBUTION_DETAIL_URL.format(balance_distribution_id=balance_distribution_id),
                                         func_description="Balance Distribution",
                                         logger=logger)
        return success