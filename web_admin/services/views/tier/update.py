import logging

from multiprocessing import Process, Manager
from django.views.generic.base import TemplateView
from django.conf import settings
from web_admin import api_settings
from django.shortcuts import redirect, render
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)


class UpdateView(TemplateView, RESTfulMethods):
    template_name = "services/tier/tier_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start Updating Tier ==========')
        context = super(UpdateView, self).get_context_data(**kwargs)
        tier_id = context['fee_tier_id']
        tier_to_update = self._get_tier_detail(tier_id)
        for i in tier_to_update:
            if tier_to_update[i] is None:
                tier_to_update[i] = 'Non'

        context['update_tier'] = tier_to_update
        service_id = context['service_id']
        command_id = context['command_id']

        manager = Manager()
        return_dict = manager.dict()

        process_get_tier_condition = Process(target=self._get_tier_condition,
                                             args=(1, return_dict))
        process_get_tier_condition.start()
        process_get_amount_types = Process(target=self._get_amount_types,
                                           args=(2, return_dict))
        process_get_amount_types.start()
        process_get_service_detail = Process(target=self._get_service_detail,
                                             args=(3, return_dict, service_id))
        process_get_service_detail.start()
        process_get_command_name = Process(target=self._get_command_name,
                                           args=(4, return_dict, command_id))
        process_get_command_name.start()

        process_get_fee_types = Process(target=self._get_fee_types, args=(5, return_dict))
        process_get_fee_types.start()
        process_get_bonus_types = Process(target=self._get_bonus_types, args=(6, return_dict))
        process_get_bonus_types.start()

        process_get_tier_condition.join()
        process_get_amount_types.join()
        process_get_service_detail.join()
        process_get_command_name.join()
        process_get_fee_types.join()
        process_get_bonus_types.join()

        tier_conditions, status1 = return_dict[1]
        amount_types, status2 = return_dict[2]
        service_detail, status3 = return_dict[3]
        command_name, status4 = return_dict[4]
        fee_types, status5 = return_dict[5]
        bonus_types, status6 = return_dict[6]

        if process_get_tier_condition.is_alive():
            process_get_tier_condition.terminate()

        if process_get_amount_types.is_alive():
            process_get_amount_types.terminate()

        if process_get_service_detail.is_alive():
            process_get_service_detail.terminate()

        if process_get_command_name.is_alive():
            process_get_command_name.terminate()

        if process_get_fee_types.is_alive():
            process_get_fee_types.terminate()

        if process_get_bonus_types.is_alive():
            process_get_bonus_types.terminate()

        if status1 and status2 and status3 and status4 and status5 and status6:
            context.update({
                'conditions': tier_conditions,
                'fee_types': fee_types,
                'bonus_types': bonus_types,
                'amount_types': amount_types,
                'service_name': service_detail.get('service_name', 'unknown'),
                'command_name': command_name,
                'update_tier': tier_to_update,
            })
        return render(request, self.template_name, context)

    def _get_tier_detail(self, tier_id):
        tier_detail, status = self._get_method(api_settings.TIER_PATH.format(tier_id),
                                              func_description="Tier Detail",
                                              logger=logger)
        return tier_detail


    def _get_tier_condition(self, procnum, dict):
        dict[procnum] = self._get_method(api_settings.FEE_TIER_CONDITION_URL,
                                               func_description="Tier Condition",
                                               logger=logger)

    def _get_amount_types(self, procnum, dict):
        dict[procnum] = self._get_method(api_settings.AMOUNT_TYPES_URL,
                                                  func_description="Amount Types",
                                                  logger=logger)

    def _get_service_detail(self, procnum, dict, service_id):
        dict[procnum] = self._get_method(api_settings.SERVICE_DETAIL_URL.format(service_id),
                                                  func_description="Service Detail",
                                                  logger=logger)


    def _get_command_name(self, procnum, dict, command_id):
        commands_list, status = self._get_method(api_settings.COMMAND_LIST_URL,
                                                 func_description="Commands List",
                                                 logger=logger)
        if status:
            command_name = None
            my_id = int(command_id)
            for x in commands_list:
                if x['command_id'] == my_id:
                    command_name = x['command_name']
                    dict[procnum] = command_name, True
                    return None
            dict[procnum] = 'Unknown', True
        else:
            dict[procnum] = None, False

    def _get_fee_types(self, procnum, dict):

        dict[procnum] = self._get_method(api_settings.GET_FEE_TYPES_PATH,
                                             func_description="Fee Types",
                                             logger=logger)

    def _get_bonus_types(self, procnum, dict):
        dict[procnum] = self._get_method(api_settings.GET_BONUS_TYPES_PATH,
                                               func_description="Bonus Types",
                                               logger=logger)


    def post(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        command_id = context['command_id']
        service_id = context['service_id']
        service_command_id = context['service_command_id']

        data = {
            "fee_tier_condition": request.POST.get('condition'),
            "condition_amount": request.POST.get('condition_amount'),
            "fee_type": request.POST.get('fee_type'),
            "fee_amount": request.POST.get('fee_amount'),
            "bonus_type": request.POST.get('bonus_type'),
            "bonus_amount": request.POST.get('bonus_amount'),
            "amount_type": request.POST.get('amount_type'),
        }

        if data['bonus_type'] == "Flat value":
            data['amount_type'] = ''

        fee_tier_id = context['fee_tier_id']

        success = self._edit_tier(fee_tier_id, data)
        self.logger.info('========== Finish Updating Tier ==========')
        if success:
            request.session['edit_tier_msg'] = 'Updated data successfully'
        return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id,
                        service_command_id=service_command_id)

    def _edit_tier(self, fee_tier_id, data):
        result, status = self._put_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                   func_description="Edit Tier",
                                   logger=logger, params=data)
        return status

