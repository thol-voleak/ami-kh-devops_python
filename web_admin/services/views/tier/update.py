import logging
from django.contrib import messages
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username

logger = logging.getLogger(__name__)


class UpdateView(TemplateView, RESTfulMethods):
    template_name = "services/tier/tier_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start Updating Tier ==========')
        decimal = 0
        context = super(UpdateView, self).get_context_data(**kwargs)
        tier_id = context['fee_tier_id']
        tier_to_update = self._get_tier_detail(tier_id)
        context['update_tier'] = tier_to_update
        service_id = context['service_id']
        command_id = context['command_id']
        tier_conditions, status1 = self._get_tier_condition()
        fee_types, status2 = self._get_fee_types()
        bonus_types, status3 = self._get_bonus_types()
        amount_types, status4 = self._get_amount_types()
        service_detail, status5 = self._get_service_detail(service_id)
        currencies = self._get_currencies_list()

        if service_detail and currencies:
            currency_name = service_detail['currency']
            if currency_name in currencies.keys():
                decimal = currencies[currency_name]

        command_name, status6 = self._get_command_name(command_id)
        if status1 and status2 and status3 and status4 and status5 and status6:
            context.update({
                'conditions': tier_conditions,
                'fee_types':  fee_types,
                'bonus_types': bonus_types,
                'amount_types': amount_types,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'update_tier': tier_to_update,
                'decimal': int(decimal),
            })

        return render(request, self.template_name, context)

    def _get_tier_detail(self, tier_id):
        tier_detail, status = self._get_precision_method(api_settings.TIER_PATH.format(tier_id),
                                                         func_description="Tier Detail",
                                                         logger=logger)
        return tier_detail

    def _get_tier_condition(self):
        return self._get_method(api_settings.FEE_TIER_CONDITION_URL,
                                func_description="Tier Condition",
                                logger=logger)

    def _get_amount_types(self):
        return self._get_method(api_settings.AMOUNT_TYPES_URL,
                                func_description="Amount Types",
                                logger=logger)

    def _get_service_detail(self, service_id):
        return self._get_method(api_settings.SERVICE_DETAIL_URL.format(service_id),
                                func_description="Service Detail",
                                logger=logger)

    def _get_command_name(self, command_id):
        commands_list, status = self._get_method(api_settings.COMMAND_LIST_URL,
                                                 func_description="Commands List",
                                                 logger=logger)
        if status:
            command_name = None
            my_id = int(command_id)
            for x in commands_list:
                if x['command_id'] == my_id:
                    command_name = x['command_name']
                    return command_name, True
            return 'Unknown', True
        else:
            return None, False

    def _get_fee_types(self):

        return self._get_method(api_settings.GET_FEE_TYPES_PATH,
                                func_description="Fee Types",
                                logger=logger)

    def _get_bonus_types(self):
        return self._get_method(api_settings.GET_BONUS_TYPES_PATH,
                                func_description="Bonus Types",
                                logger=logger)

    def post(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        command_id = context['command_id']
        service_id = context['service_id']
        service_command_id = context['service_command_id']

        condition_amount = request.POST.get('condition_amount', '')
        settlement_type = request.POST.get('settlement_type', '')
        condition = request.POST.get('condition', '')
        fee_type = request.POST.get('fee_type')
        bonus_type = request.POST.get('bonus_type')
        amount_type = request.POST.get('amount_type')

        if condition_amount:
            condition_amount = condition_amount.replace(',', '')
        fee_amount = request.POST.get('fee_amount')
        if fee_amount:
            fee_amount = fee_amount.replace(',', '')
        bonus_amount = request.POST.get('bonus_amount')
        if bonus_amount:
            bonus_amount = bonus_amount.replace(',', '')

        params = {
            "fee_tier_condition": condition,
            "condition_amount": condition_amount,
            "fee_type": fee_type,
            "fee_amount": fee_amount,
            "bonus_type": bonus_type,
            "bonus_amount": bonus_amount,
            "amount_type": amount_type,
            "settlement_type": settlement_type
        }

        if params['bonus_type'] == "Flat value":
            params['amount_type'] = ''

        fee_tier_id = context['fee_tier_id']

        data, success = self._edit_tier(fee_tier_id, params)
        self.logger.info('========== Finish Updating Tier ==========')
        if success:
            request.session['edit_tier_msg'] = 'Updated data successfully'
            return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )

            decimal = 0
            context = super(UpdateView, self).get_context_data(**kwargs)
            service_id = context['service_id']
            command_id = context['command_id']
            tier_conditions, status1 = self._get_tier_condition()
            fee_types, status2 = self._get_fee_types()
            bonus_types, status3 = self._get_bonus_types()
            amount_types, status4 = self._get_amount_types()
            service_detail, status5 = self._get_service_detail(service_id)
            currencies = self._get_currencies_list()
            if service_detail and currencies:
                currency_name = service_detail['currency']
                if currency_name in currencies.keys():
                    decimal = currencies[currency_name]
            command_name, status6 = self._get_command_name(command_id)
            if status1 and status2 and status3 and status4 and status5 and status6:
                context.update({
                    'conditions': tier_conditions,
                    'fee_types': fee_types,
                    'bonus_types': bonus_types,
                    'amount_types': amount_types,
                    'service_name': service_detail.get('service_name', 'unknown'),
                    'command_name': command_name,
                    'decimal': int(decimal),
                    'update_tier': params
                })

            return render(request, self.template_name, context)

    def _edit_tier(self, fee_tier_id, data):
        return self._put_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                func_description="Edit Tier",
                                logger=logger, params=data)

    def _get_currencies_list(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list",
                                         logger=logger,
                                         is_getting_list=True)
        if data:
            value = data.get('value', '')
            currencies = value.split(',')
            curr_dict = {i.split('|')[0]: i.split('|')[1] for i in currencies}
            return curr_dict
        else:
            return {}
