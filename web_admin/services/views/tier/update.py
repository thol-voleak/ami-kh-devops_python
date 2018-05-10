import logging
from django.contrib import messages
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username
from web_admin.api_logger import API_Logger
from services.views.tier_levels.utils import get_label_levels

logger = logging.getLogger(__name__)


class UpdateView(TemplateView, RESTfulMethods):
    template_name = "services/tier/tier_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start Loading updating Tier Page==========')
        decimal = 0
        context = super(UpdateView, self).get_context_data(**kwargs)
        tier_id = context['fee_tier_id']
        tier_to_update = self._get_tier_detail(tier_id)
        context['update_tier'] = tier_to_update
        service_id = context['service_id']
        command_id = context['command_id']
        tier_conditions, status1 = self._get_tier_condition()
        self.logger.info('========== Finish get Tier condition ==========')
        fee_types, status2 = self._get_fee_types()
        self.logger.info('========== Finish get fee types ==========')
        bonus_types, status3 = self._get_bonus_types()
        self.logger.info('========== Finish get bonus types ==========')
        amount_types, status4 = self._get_amount_types()
        self.logger.info('========== Finish get amount type ==========')
        service_detail, status5 = self._get_service_detail(service_id)
        self.logger.info('========== Finish get service detail ==========')
        tier_amount_froms, status7 = self._get_tier_amount_froms()
        self.logger.info('========== Finish get tier amount froms ==========')
        payment_decimals, status8 = self._get_payment_decimal()
        self.logger.info('========== Finish get payment decimal ==========')
        currencies = self._get_currencies_list()

        if service_detail and currencies:
            currency_name = service_detail['currency']
            if currency_name in currencies.keys():
                decimal = currencies[currency_name]

        payment_decimal = payment_decimals['value']

        a_label = self.get_label_detail('A')
        b_label = self.get_label_detail('B')
        c_label = self.get_label_detail('C')
        d_label = self.get_label_detail('D')
        e_label = self.get_label_detail('E')
        f_label = self.get_label_detail('F')
        g_label = self.get_label_detail('G')
        h_label = self.get_label_detail('H')
        i_label = self.get_label_detail('I')
        j_label = self.get_label_detail('J')
        k_label = self.get_label_detail('K')
        l_label = self.get_label_detail('L')
        m_label = self.get_label_detail('M')
        n_label = self.get_label_detail('N')
        o_label = self.get_label_detail('O')

        command_name, status6 = self._get_command_name(command_id)
        if status1 and status2 and status3 and status4 and status5 and status6 and status7 and status8:
            context.update({
                'conditions': tier_conditions,
                'fee_types':  fee_types,
                'bonus_types': bonus_types,
                'tier_amount_froms': tier_amount_froms,
                'amount_types': amount_types,
                'payment_decimal': payment_decimal,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'update_tier': tier_to_update,
                'a_label': a_label,
                'b_label': b_label,
                'c_label': c_label,
                'd_label': d_label,
                'e_label': e_label,
                'f_label': f_label,
                'g_label': g_label,
                'h_label': h_label,
                'i_label': i_label,
                'j_label': j_label,
                'k_label': k_label,
                'l_label': l_label,
                'm_label': m_label,
                'n_label': n_label,
                'o_label': o_label,
                'decimal': int(decimal),
            })
        self.logger.info('========== Finish Loading updating Tier Page==========')
        return render(request, self.template_name, context)

    def _get_tier_detail(self, tier_id):
        self.logger.info('========== Start get Tier detail ==========')
        tier_detail, status = self._get_precision_method(api_settings.TIER_PATH.format(tier_id),
                                                         func_description="Tier Detail",
                                                         logger=logger)
        self.logger.info('========== Finish get Tier detail ==========')
        return tier_detail

    def _get_tier_condition(self):
        self.logger.info('========== Start get Tier condition ==========')
        return self._get_method(api_settings.FEE_TIER_CONDITION_URL,
                                func_description="Tier Condition",
                                logger=logger)

    def _get_amount_types(self):
        self.logger.info('========== Start get amount type ==========')
        return self._get_method(api_settings.AMOUNT_TYPES_URL,
                                func_description="Amount Types",
                                logger=logger)

    def _get_service_detail(self, service_id):
        self.logger.info('========== Start get service detail ==========')
        return self._get_method(api_settings.SERVICE_DETAIL_URL.format(service_id),
                                func_description="Service Detail",
                                logger=logger)

    def _get_tier_amount_froms(self):
        self.logger.info('========== Start get tier amount froms ==========')
        return self._get_method(api_settings.TIER_AMOUNT_FROMS,
                                func_description="Tier amount froms",
                                logger=logger)

    def _get_payment_decimal(self):
        self.logger.info('========== Start get payment decimal ==========')
        return self._get_method(api_settings.PAYMENT_DECIMAL,
                                func_description="Payment decimal",
                                logger=logger)

    def _get_command_name(self, command_id):
        self.logger.info('========== Start get command name ==========')
        commands_list, status = self._get_method(api_settings.COMMAND_LIST_URL,
                                                 func_description="Commands List",
                                                 logger=logger)
        self.logger.info('========== Finish get command name ==========')
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
        self.logger.info('========== Start get fee types ==========')
        return self._get_method(api_settings.GET_FEE_TYPES_PATH,
                                func_description="Fee Types",
                                logger=logger)

    def _get_bonus_types(self):
        self.logger.info('========== Start get bonus types ==========')
        return self._get_method(api_settings.GET_BONUS_TYPES_PATH,
                                func_description="Bonus Types",
                                logger=logger)

    def post(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        self.logger.info('========== Start updating Tier==========')
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

        a = request.POST.get('a')
        a_from = request.POST.get('a_from')
        a_amount = request.POST.get('a_amount')
        b = request.POST.get('b')
        b_from = request.POST.get('b_from')
        b_amount = request.POST.get('b_amount')
        c = request.POST.get('c')
        c_from = request.POST.get('c_from')
        c_amount = request.POST.get('c_amount')
        d = request.POST.get('d')
        d_from = request.POST.get('d_from')
        d_amount = request.POST.get('d_amount')
        e = request.POST.get('e')
        e_from = request.POST.get('e_from')
        e_amount = request.POST.get('e_amount')
        f = request.POST.get('f')
        f_from = request.POST.get('f_from')
        f_amount = request.POST.get('f_amount')
        g = request.POST.get('g')
        g_from = request.POST.get('g_from')
        g_amount = request.POST.get('g_amount')
        h = request.POST.get('h')
        h_from = request.POST.get('h_from')
        h_amount = request.POST.get('h_amount')
        i = request.POST.get('i')
        i_from = request.POST.get('i_from')
        i_amount = request.POST.get('i_amount')
        j = request.POST.get('j')
        j_from = request.POST.get('j_from')
        j_amount = request.POST.get('j_amount')
        k = request.POST.get('k')
        k_from = request.POST.get('k_from')
        k_amount = request.POST.get('k_amount')
        l = request.POST.get('l')
        l_from = request.POST.get('l_from')
        l_amount = request.POST.get('l_amount')
        m = request.POST.get('m')
        m_from = request.POST.get('m_from')
        m_amount = request.POST.get('m_amount')
        n = request.POST.get('n')
        n_from = request.POST.get('n_from')
        n_amount = request.POST.get('n_amount')
        o = request.POST.get('o')
        o_from = request.POST.get('o_from')
        o_amount = request.POST.get('o_amount')

        params = {
            "fee_tier_condition": condition,
            "condition_amount": condition_amount,
            "fee_type": fee_type,
            "fee_amount": fee_amount,
            "bonus_type": bonus_type,
            "bonus_amount": bonus_amount,
            "amount_type": amount_type,
            "settlement_type": settlement_type,
            "a": a,
            "a_from": a_from,
            "a_amount": a_amount,
            "b": b,
            "b_from": b_from,
            "b_amount": b_amount,
            "c": c,
            "c_from": c_from,
            "c_amount": c_amount,
            "d": d,
            "d_from": d_from,
            "d_amount": d_amount,
            "e": e,
            "e_from": e_from,
            "e_amount": e_amount,
            "f": f,
            "f_from": f_from,
            "f_amount": f_amount,
            "g": g,
            "g_from": g_from,
            "g_amount": g_amount,
            "h": h,
            "h_from": h_from,
            "h_amount": h_amount,
            "i": i,
            "i_from": i_from,
            "i_amount": i_amount,
            "j": j,
            "j_from": j_from,
            "j_amount": j_amount,
            "k": k,
            "k_from": k_from,
            "k_amount": k_amount,
            "l": l,
            "l_from": l_from,
            "l_amount": l_amount,
            "m": m,
            "m_from": m_from,
            "m_amount": m_amount,
            "n": n,
            "n_from": n_from,
            "n_amount": n_amount,
            "o": o,
            "o_from": o_from,
            "o_amount": o_amount
        }

        if params['bonus_type'] == "Flat value" or params['bonus_type'] == "":
            params['amount_type'] = ''
        if params['a'] == "Flat value" or params['a'] == "":
            params['a_from'] = None
        if params['b'] == "Flat value" or params['b'] == "":
            params['b_from'] = None
        if params['c'] == "Flat value" or params['c'] == "":
            params['c_from'] = None
        if params['d'] == "Flat value" or params['d'] == "":
            params['d_from'] = None
        if params['e'] == "Flat value" or params['e'] == "":
            params['e_from'] = None
        if params['f'] == "Flat value" or params['f'] == "":
            params['f_from'] = None
        if params['g'] == "Flat value" or params['g'] == "":
            params['g_from'] = None
        if params['h'] == "Flat value" or params['h'] == "":
            params['h_from'] = None
        if params['i'] == "Flat value" or params['i'] == "":
            params['i_from'] = None
        if params['j'] == "Flat value" or params['j'] == "":
            params['j_from'] = None
        if params['k'] == "Flat value" or params['k'] == "":
            params['k_from'] = None
        if params['l'] == "Flat value" or params['l'] == "":
            params['l_from'] = None
        if params['m'] == "Flat value" or params['m'] == "":
            params['m_from'] = None
        if params['n'] == "Flat value" or params['n'] == "":
            params['n_from'] = None
        if params['o'] == "Flat value" or params['o'] == "":
            params['o_from'] = None

        fee_tier_id = context['fee_tier_id']

        if bonus_type == 'Flat value' and condition != 'unlimit' and self.is_float(bonus_amount) and self.is_float(condition_amount):
            amount_number = float(condition_amount)
            bonus_amount_number = float(bonus_amount)
            if amount_number < bonus_amount_number:
                messages.add_message(
                    request,
                    messages.ERROR,
                    message="Bonus Amount cannot be greater than the Amount"
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
        self.logger.info('========== Start get currencies list ==========')
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list",
                                         logger=logger,
                                         is_getting_list=True)
        self.logger.info('========== Finish get currencies list ==========')
        if data:
            value = data.get('value', '')
            currencies = value.split(',')
            curr_dict = {i.split('|')[0]: i.split('|')[1] for i in currencies}
            return curr_dict
        else:
            return {}
        return {}

    def is_float(self, input_number):
        try:
            num = float(input_number)
        except Exception:
            return False
        return True

    def get_label_detail(self, lvl_name):
        label_levels = self.request.session.get('tier_levels')
        if not label_levels:
            label_levels = get_label_levels(self.request)

        for lvl in label_levels:
            if lvl.get('name') == lvl_name:
                return lvl.get('label')
