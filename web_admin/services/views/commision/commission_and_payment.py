import logging
import json
from web_admin.api_settings import SEARCH_AGENT
from multiprocessing.pool import ThreadPool
from django.conf import settings
from web_admin import api_settings, setup_logger
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from services.views.mixins import GetCommandNameAndServiceNameMixin
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
from services.views.utils import get_payment_decimal, get_currency_by_service_id
from services.views.tier_levels.utils import get_label_levels


logger = logging.getLogger(__name__)


class CommissionAndPaymentView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission/commission_and_payment.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CommissionAndPaymentView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CommissionAndPaymentView, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        self.logger.info('========== Start getting Balance Movement ==========')

        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')

        #self.logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

        self.logger.info('========== Start getting Fee Tier Detail ==========')
        fee_tier_detail, success = self._get_fee_tier_detail(tier_id)
        self.logger.info('========== Finish getting Fee Tier Detail ==========')

        self.logger.info('========== Start getting Setting Payment, Fee & Bonus Structure ==========')
        data, success = self._get_commission_and_payment_list(tier_id)
        self.logger.info('========== Finish getting Setting Payment, Fee & Bonus Structure ==========')

        #bonus, success = self._get_setting_bonus_list(tier_id)

        # agent_bonus_distribution, success = self._get_agent_bonus_distribution_list(tier_id)
        # total_bonus_distribution = self._filter_deleted_items(agent_bonus_distribution)

        #fee, success = self._get_agent_fee_distribution_list(tier_id)
        self.logger.info('========== Start getting options for Setting Payment, Fee & Bonus Structure ==========')
        choices = self._get_choices(command_id)
        specific_ids = self._get_specific_ids()
        self.logger.info('========== Finish getting options for Setting Payment, Fee & Bonus Structure ==========')
        #agents = self._get_agents()

        if specific_ids and isinstance(specific_ids, list):
            context['specific_ids'] = specific_ids
        else:
            context['specific_ids'] = []
            self.logger.error('Error when getting Specific IDs: {}'.format(specific_ids))

        context['fee_tier_detail'] = fee_tier_detail

        tiers_conf = [
            {'type': fee_tier_detail['fee_type'], 'amount': fee_tier_detail['fee_amount']},
            {'type': fee_tier_detail['bonus_type'], 'from': fee_tier_detail['amount_type'], 'amount': fee_tier_detail['bonus_amount']},
            {'type': fee_tier_detail['a'], 'label': self.get_label_detail('A'), 'from': fee_tier_detail['a_from'], 'amount': fee_tier_detail['a_amount']},
            {'type': fee_tier_detail['b'], 'label': self.get_label_detail('B'), 'from': fee_tier_detail['b_from'], 'amount': fee_tier_detail['b_amount']},
            {'type': fee_tier_detail['c'], 'label': self.get_label_detail('C'), 'from': fee_tier_detail['c_from'], 'amount': fee_tier_detail['c_amount']},
            {'type': fee_tier_detail['d'], 'label': self.get_label_detail('D'), 'from': fee_tier_detail['d_from'], 'amount': fee_tier_detail['d_amount']},
            {'type': fee_tier_detail['e'], 'label': self.get_label_detail('E'), 'from': fee_tier_detail['e_from'], 'amount': fee_tier_detail['e_amount']},
            {'type': fee_tier_detail['f'], 'label': self.get_label_detail('F'), 'from': fee_tier_detail['f_from'], 'amount': fee_tier_detail['f_amount']},
            {'type': fee_tier_detail['g'], 'label': self.get_label_detail('G'), 'from': fee_tier_detail['g_from'], 'amount': fee_tier_detail['g_amount']},
            {'type': fee_tier_detail['h'], 'label': self.get_label_detail('H'), 'from': fee_tier_detail['h_from'], 'amount': fee_tier_detail['h_amount']},
            {'type': fee_tier_detail['i'], 'label': self.get_label_detail('I'), 'from': fee_tier_detail['i_from'], 'amount': fee_tier_detail['i_amount']},
            {'type': fee_tier_detail['j'], 'label': self.get_label_detail('J'), 'from': fee_tier_detail['j_from'], 'amount': fee_tier_detail['j_amount']},
            {'type': fee_tier_detail['k'], 'label': self.get_label_detail('K'), 'from': fee_tier_detail['k_from'], 'amount': fee_tier_detail['k_amount']},
            {'type': fee_tier_detail['l'], 'label': self.get_label_detail('L'), 'from': fee_tier_detail['l_from'], 'amount': fee_tier_detail['l_amount']},
            {'type': fee_tier_detail['m'], 'label': self.get_label_detail('M'), 'from': fee_tier_detail['m_from'], 'amount': fee_tier_detail['m_amount']},
            {'type': fee_tier_detail['n'], 'label': self.get_label_detail('N'), 'from': fee_tier_detail['n_from'], 'amount': fee_tier_detail['n_amount']},
            {'type': fee_tier_detail['o'], 'label': self.get_label_detail('O'), 'from': fee_tier_detail['o_from'], 'amount': fee_tier_detail['o_amount']},
        ]

        valid_tiers_conf = self.check_valid_tier(tiers_conf)

        context['valid_tiers_conf'] = valid_tiers_conf

        self._replace_actor_type_items(data)
        self._replace_amount_type_items(data)
        context['data'] = self._filter_deleted_items(data)
        #context['bonus'] = self._filter_deleted_items(bonus)
        #context['agent_bonus_distribution'] = total_bonus_distribution
        #context['fee'] = self._filter_deleted_items(fee)
        context['choices'] = choices
        #context['agents'] = agents

        response = get_payment_decimal(self.request)
        if response:
            context['payment_decimal'] = response.get('value')

        get_currency_by_service_id(self.request, service_id)

        self.logger.info('========== Finish getting Balance Movement ==========')
        return context

    def check_valid_tier(self, tiers):
        valid_tiers = []
        for tier in tiers:
            for i in tier:
                if i != 'label' and tier[i] and tier[i] != 'NON':
                    valid_tiers.append(tier)
                    break
        return valid_tiers

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

    def _replace_actor_type_items(self, data):
        for balance_distribution in data:
            if balance_distribution['actor_type'] in ['Grand Parent', 'Parent']:
                balance_distribution['actor_type'] = None

    def _replace_amount_type_items(self, data):
        for balance_distribution in data:
            if balance_distribution['amount_type'] == 'Parent Fee Rate':
                balance_distribution['amount_type'] = None

    def _get_choices(self, command_id):
        url_list = [api_settings.ACTION_TYPES_URL, api_settings.AMOUNT_TYPES_URL,
                    api_settings.SOF_TYPES_URL, api_settings.ACTOR_TYPES_URL]
        pool = ThreadPool(processes=1)

        async_list = map(lambda url: pool.apply_async(lambda: self._get_choices_types(url)),
                         url_list)
        result_list = list(map(lambda x: x.get(), async_list))

        if command_id == '2':
            result_list[3] = [i for i in result_list[3] if 'Beneficiary' not in i['actor_type']]

        return {
            'action_types': result_list[0],
            'amount_types': result_list[1],
            'sof_types': result_list[2],
            'actor_types': result_list[3],
        }

    def _get_choices_types(self, url):
        data, success = self._get_method(api_path=url,
                                     func_description="Choices Type",
                                     logger=logger)
        return data

    def _get_fee_tier_detail(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment, Fee & Bonus Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(api_path=api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
                                         func_description="Agent bonus distribution",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Agent Fee Distribution List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agents(self):
        self.logger.info('========== Start searching agent ==========')

        api_path = SEARCH_AGENT
        data, status = self._post_method(
            api_path=api_path,
            func_description="Search Agent",
            logger=logger,
            params={}
        )

        self.logger.info('========== Finished searching agent ==========')
        return data

    def get_label_detail(self, lvl_name):
        label_levels = self.request.session.get('tier_levels')
        if not label_levels:
            label_levels = get_label_levels(self.request)

        for lvl in label_levels:
            if lvl.get('name') == lvl_name:
                return lvl.get('label')

class PaymentAndFeeStructureView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission/commission_and_payment.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PaymentAndFeeStructureView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PaymentAndFeeStructureView, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        self.logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

        fee_tier_detail, success = self._get_fee_tier_detail(tier_id)

        data, success = self._get_commission_and_payment_list(tier_id)

        bonus, success = self._get_setting_bonus_list(tier_id)

        agent_bonus_distribution, success = self._get_agent_bonus_distribution_list(tier_id)
        total_bonus_distribution = self._filter_deleted_items(agent_bonus_distribution)

        fee, success = self._get_agent_fee_distribution_list(tier_id)
        choices = self._get_choices()
        specific_ids = self._get_specific_ids()

        context['specific_ids'] = specific_ids
        context['fee_tier_detail'] = fee_tier_detail
        context['data'] = self._filter_deleted_items(data)
        context['bonus'] = self._filter_deleted_items(bonus)
        context['agent_bonus_distribution'] = total_bonus_distribution
        context['fee'] = self._filter_deleted_items(fee)
        context['choices'] = choices
        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')
        return context

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

    def _get_choices(self):
        url_list = [api_settings.ACTION_TYPES_URL, api_settings.AMOUNT_TYPES_URL,
                    api_settings.SOF_TYPES_URL, api_settings.ACTOR_TYPES_URL]
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
        data, success = self._get_method(api_path=url,
                                         func_description="Choices Type",
                                         logger=logger)
        return data

    def _get_fee_tier_detail(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment, Fee & Bonus Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
            func_description="Agent bonus distribution",
            logger=logger,
            is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
            func_description="Agent Fee Distribution List",
            logger=logger,
            is_getting_list=True)
        return data, success

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.DOMAIN_NAMES + api_settings.TIER_DETAIL_URL.format(fee_tier_id=fee_tier_id)

        self.logger.info('========== Start create Setting Payment, Fee & Bonus Structure ==========')

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "remark": data.get("remark"),
            "specific_actor_id": data.get("specific_actor_id"),
        }

        response, status = self._post_method(api_path=url,
                                   func_description="create Setting Payment, Fee & Bonus Structure",
                                   logger=logger, params=post_data)

        if status:
            msg = 'Added Setting Payment, Fee & Bonus Structure successfully'
            if msg not in [m.message for m in messages.get_messages(request)]:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    msg
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                response
            )
        self.logger.info('========== Finish create Setting Payment, Fee & Bonus Structure ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)


class BalanceDistributionsUpdate(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceDistributionsUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating Setting Payment, Fee & Bonus Structure ==========")

        balance_distribution_id = kwargs.get('balance_distributions_id')
        url = api_settings.BALANCE_DISTRIBUTION_UPDATE_URL.format(balance_distribution_id=balance_distribution_id)

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
            "remark": data.get("remark"),
            # "specific_actor_id": data.get("specific_actor_id"),
        }

        response = ajax_functions._put_method(request, url, "", self.logger, post_data)
        self.logger.info("========== Finished updating Setting Payment, Fee & Bonus Structure ==========")
        return response


class BonusDistributionsUpdate(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BonusDistributionsUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start update setting bonus ==========")

        bonus_distributions_id = kwargs.get('bonus_distributions_id')

        url = api_settings.BONUS_DISTRIBUTION_UPDATE_URL.format(bonus_distributions_id=bonus_distributions_id)

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

        response = ajax_functions._put_method(request, url, "", self.logger, post_data)
        self.logger.info("========== Finish update setting bonus ==========")
        return response

class AgentBonusDistributionsUpdate(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentBonusDistributionsUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating agent bonus distribution ==========")

        agent_bonus_distribution_id = kwargs.get('agent_bonus_distribution_id')
        url = api_settings.AGENT_BONUS_DISTRIBUTION_UPDATE_URL.format(agent_bonus_distribution_id=agent_bonus_distribution_id)

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

        response = ajax_functions._put_method(request, url, "", self.logger, post_data)
        self.logger.info("========== Finished updating agent bonus distribution ==========")

        return response

class SettingBonusView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission/commission_and_payment.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SettingBonusView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SettingBonusView, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        self.logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

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
        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')
        return context

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

    def _get_choices(self):
        url_list = [api_settings.ACTION_TYPES_URL, api_settings.AMOUNT_TYPES_URL,
                    api_settings.SOF_TYPES_URL, api_settings.ACTOR_TYPES_URL]
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
        data, success = self._get_method(api_path=url,
                                         func_description="Choices Type",
                                         logger=logger)
        return data

    def _get_fee_tier_detail(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment, Fee & Bonus Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
            func_description="Agent bonus distribution",
            logger=logger,
            is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
            func_description="Agent Fee Distribution List",
            logger=logger,
            is_getting_list=True)
        return data, success

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.DOMAIN_NAMES + api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        self.logger.info('========== Start create Setting Bonus ==========')

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

        response, status = self._post_method(api_path=url,
                                             func_description="create Setting Bonus",
                                             logger=logger, params=post_data)

        if status:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added setting bonus successfully'
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                response
            )

        self.logger.info('========== Finish create Setting Bonus ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)

class PaymentAndFeeStructureDetailView(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PaymentAndFeeStructureDetailView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting Setting Payment, Fee & Bonus Structure ==========')
        balance_distribution_id = kwargs.get('balance_distribution_id')

        url = api_settings.BALANCE_DISTRIBUTION_DETAIL_URL.format(balance_distribution_id=balance_distribution_id)
        response = ajax_functions._delete_method(request, url, "", self.logger)
        self.logger.info('========== Finish deleting Setting Payment, Fee & Bonus Structure ==========')
        return response

class AgentFeeView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission/commission_and_payment.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentFeeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AgentFeeView, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        self.logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

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
        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')
        return context

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

    def _get_choices(self):
        url_list = [api_settings.ACTION_TYPES_URL, api_settings.AMOUNT_TYPES_URL,
                    api_settings.SOF_TYPES_URL, api_settings.ACTOR_TYPES_URL]
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
        data, success = self._get_method(api_path=url,
                                         func_description="Choices Type",
                                         logger=logger)
        return data

    def _get_fee_tier_detail(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment, Fee & Bonus Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
            func_description="Agent bonus distribution",
            logger=logger,
            is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
            func_description="Agent Fee Distribution List",
            logger=logger,
            is_getting_list=True)
        return data, success

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        self.logger.info('========== Start create Agent Hierarchy Fee ==========')

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof_add'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("add_rate"),
            "specific_actor_id": data.get("specific_actor_id"),
            "is_deleted": 0
        }

        # import pdb;
        # pdb.set_trace()

        if post_data['actor_type'] != 'Specific ID':
            post_data['specific_actor_id'] = ''

        response, status = self._post_method(api_path=url,
                                             func_description="create Agent Hierarchy Fee",
                                             logger=logger, params=post_data)

        if status:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added Agent Hierarchy Distribution - Fee successfully'
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                response
            )

        self.logger.info('========== Finish create Agent Hierarchy Fee list ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)


class AgentBonusDistributions(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/commission/commission_and_payment.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentBonusDistributions, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AgentBonusDistributions, self).get_context_data(*args, **kwargs)
        command_id = kwargs.get('command_id')
        service_id = kwargs.get('service_id')
        tier_id = kwargs.get('fee_tier_id')
        if not tier_id:
            raise Http404

        self.logger.info('Get CommissionAndPaymentView by user: {}'.format(self.request.user.username))

        fee_tier_detail, success = self._get_fee_tier_detail(tier_id)

        data, success = self._get_commission_and_payment_list(tier_id)

        bonus, success = self._get_setting_bonus_list(tier_id)

        agent_bonus_distribution, success = self._get_agent_bonus_distribution_list(tier_id)
        total_bonus_distribution = self._filter_deleted_items(agent_bonus_distribution)

        fee, success = self._get_agent_fee_distribution_list(tier_id)
        choices = self._get_choices()

        specific_ids = self._get_specific_ids()
        if specific_ids and isinstance(specific_ids, list):
            context['specific_ids'] = specific_ids
        else:
            context['specific_ids'] = []
            self.logger.error('Error when getting Specific IDs: {}'.format(specific_ids))
            
        context['fee_tier_detail'] = fee_tier_detail
        context['data'] = self._filter_deleted_items(data)
        context['bonus'] = self._filter_deleted_items(bonus)
        context['agent_bonus_distribution'] = total_bonus_distribution
        context['fee'] = self._filter_deleted_items(fee)
        context['choices'] = choices
        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')
        return context

    def _filter_deleted_items(self, data):
        return list(filter(lambda x: not x['is_deleted'], data))

    def _get_choices(self):
        url_list = [api_settings.ACTION_TYPES_URL, api_settings.AMOUNT_TYPES_URL,
                    api_settings.SOF_TYPES_URL, api_settings.ACTOR_TYPES_URL]
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
        data, success = self._get_method(api_path=url,
                                         func_description="Choices Type",
                                         logger=logger)
        return data

    def _get_fee_tier_detail(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                         func_description="Fee Tier Detail",
                                         logger=logger)
        return data, success

    def _get_commission_and_payment_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BALANCE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Payment, Fee & Bonus Structure from list url",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_setting_bonus_list(self, fee_tier_id):
        data, success = self._get_method(api_path=api_settings.BONUS_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
                                         func_description="Setting Bonus List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def _get_agent_bonus_distribution_list(self, tf_fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id),
            func_description="Agent bonus distribution",
            logger=logger,
            is_getting_list=True)
        return data, success

    def _get_agent_fee_distribution_list(self, fee_tier_id):
        data, success = self._get_method(
            api_path=api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id),
            func_description="Agent Fee Distribution List",
            logger=logger,
            is_getting_list=True)
        return data, success


    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start add agent hierarchy distribution bonus ==========')
        service_id = kwargs.get('service_id')
        tf_fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        url = api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id)

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

        response, status = self._post_method(api_path=url,
                                   func_description="Add Agent Hierarchy Distribution Bonus",
                                   logger=logger, params=post_data)

        if status:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added Agent Hierarchy Distribution - Bonus Successfully'
            )
        else:
            self.logger.info("Response body for add agent hierarchy distribution bonus is {}".format(response))
            messages.add_message(
                request,
                messages.ERROR,
                response
            )
        self.logger.info('========== Finish add agent hierarchy distribution bonus  ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=tf_fee_tier_id)

class MultiBalanceDistributionsUpdate(TemplateView):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(MultiBalanceDistributionsUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating Setting Payment, Fee & Bonus Structure ==========")
        fee_tier_id = kwargs.get('fee_tier_id')
        url = api_settings.TIER_DETAIL_URL.format(fee_tier_id=fee_tier_id)

        data = request.POST.copy()
        balanceDistributionList = json.loads(data.get("balance_distributions"))
        putDataList = []
        for balanceDistributionData in balanceDistributionList:
            data = {
                "fee_tier_id": balanceDistributionData.get("fee_tier_id"),
                "balance_distribution_id": balanceDistributionData.get("balance_distribution_id"),
                "action_type": balanceDistributionData.get("action_type"),
                "actor_type": balanceDistributionData.get("actor_type"),
                "specific_actor_id": balanceDistributionData.get("specific_actor_id"),
                "sof_type_id": balanceDistributionData.get("sof_type_id"),
                "specific_sof": balanceDistributionData.get("specific_sof"),
                "amount_type": balanceDistributionData.get("amount_type"),
                "rate": balanceDistributionData.get("rate"),
                "remark": balanceDistributionData.get("remark")
            }

            putDataList.append(data)

        body = {
            "balance_distributions": putDataList
        }
        response = ajax_functions._put_method(request, url, "", self.logger, body)
        if json.loads(response.content)['status'] == 2:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Saved Setting Payment, Fee & Bonus Structure successfully"
            )
        self.logger.info("========== Finished updating Setting Payment, Fee & Bonus Structure ==========")
        return response
