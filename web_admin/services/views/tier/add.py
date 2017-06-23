import logging

from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from django.contrib import messages
logger = logging.getLogger(__name__)


class AddView(TemplateView,RESTfulMethods):
    template_name = "services/tier/tier_add.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start Adding Tier ==========')
        decimal = 0
        context = super(AddView, self).get_context_data(**kwargs)
        service_id = context['service_id']
        command_id = context['command_id']
        tier_conditions, status1 = self._get_tier_condition()
        amount_types, status2 = self._get_amount_types()
        service_detail, status3 = self._get_service_detail(service_id)
        currencies = self._get_currencies_list()
        if service_detail and currencies:
            currency_name = service_detail['currency']
            if currency_name in currencies.keys():
                decimal = currencies[currency_name]
        command_name, status4 = self._get_command_name(command_id)
        fee_types, status5 = self._get_fee_types()
        bonus_types, status6 = self._get_bonus_types()
        if status1 and status2 and status3 and status4 and status5 and status6:
            context.update({
                'conditions': tier_conditions,
                'fee_types': fee_types,
                'bonus_types': bonus_types,
                'amount_types': amount_types,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'decimal':int(decimal),
            })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)
        command_id = kwargs['command_id']
        service_id = kwargs['service_id']
        service_command_id = kwargs['service_command_id']
        condition_amount = request.POST.get('condition_amount')
        if condition_amount:
            condition_amount = condition_amount.replace(',', '')
        fee_amount = request.POST.get('fee_amount')
        if fee_amount:
            fee_amount = fee_amount.replace(',', '')
        bonus_amount = request.POST.get('bonus_amount')
        if bonus_amount:
            bonus_amount = bonus_amount.replace(',', '')

        params = {
            "fee_tier_condition": request.POST.get('condition'),
            "condition_amount": condition_amount,
            "fee_type": request.POST.get('fee_type'),
            "fee_amount": fee_amount,
            "bonus_type": request.POST.get('bonus_type'),
            "bonus_amount": bonus_amount,
        }

        if(request.POST.get('bonus_type') != 'Flat value'):
            params['amount_type'] = request.POST.get('amount_type')
        data, success = self._add_tier(service_command_id, params)
        self.logger.info('========== Finish Adding Tier ==========')
        if success:
            request.session['add_tier_msg'] = 'Added data successfully'
            return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )
            decimal = 0
            tier_conditions, status1 = self._get_tier_condition()
            amount_types, status2 = self._get_amount_types()
            service_detail, status3 = self._get_service_detail(service_id)
            currencies = self._get_currencies_list()
            if service_detail and currencies:
                currency_name = service_detail['currency']
                if currency_name in currencies.keys():
                    decimal = currencies[currency_name]
            command_name, status4 = self._get_command_name(command_id)
            fee_types, status5 = self._get_fee_types()
            bonus_types, status6 = self._get_bonus_types()
            if status1 and status2 and status3 and status4 and status5 and status6:
                context.update({
                    'conditions': tier_conditions,
                    'fee_types': fee_types,
                    'bonus_types': bonus_types,
                    'amount_types': amount_types,
                    'service_name': service_detail.get('service_name', 'unknown'),
                    'command_name': command_name,
                    'decimal': int(decimal),
                    'body':params
                })
            return render(request, self.template_name, context)



    def _add_tier(self, service_command_id, data):
        return self._post_method(api_path=api_settings.ADD_TIER_URL.format(service_command_id=service_command_id),
                                                   func_description="Adding Tier",
                                                   logger=logger, params=data)

    def _get_tier_condition(self):
        tier_conditions, status = self._get_method(api_path=api_settings.FEE_TIER_CONDITION_URL,
                                         func_description="Fee Tier Condition",
                                         logger=logger)
        return tier_conditions, status

    def _get_amount_types(self):
        amount_types, status = self._get_method(api_path=api_settings.AMOUNT_TYPES_URL,
                                         func_description="Amount Types",
                                         logger=logger)
        return amount_types, status

    def _get_service_detail(self, service_id):
        service_detail, status = self._get_method(api_settings.SERVICE_DETAIL_URL.format(service_id),
                                         func_description="Service Detail",
                                         logger=logger)
        return service_detail, status

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
        fee_types, status = self._get_method(api_settings.GET_FEE_TYPES_PATH,
                                                  func_description="Fee Types",
                                                  logger=logger)
        return fee_types, status

    def _get_bonus_types(self):
        bonus_types, status = self._get_method(api_settings.GET_BONUS_TYPES_PATH,
                                             func_description="Bonus Types",
                                             logger=logger)
        return bonus_types, status

    def _get_currencies_list(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list",
                                         logger=logger,
                                         is_getting_list=True)
        if data:
            value = data.get('value', '')
            currencies = value.split(',')
            curr_dict = {i.split('|')[0]:i.split('|')[1] for i in currencies}
            return curr_dict
        else:
            return {}

        

