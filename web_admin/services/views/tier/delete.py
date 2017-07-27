import logging

from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from .update import UpdateView
from authentications.utils import get_correlation_id_from_username
logger = logging.getLogger(__name__)


class TierDeleteView(UpdateView):
    template_name = 'services/tier/tier_delete.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(TierDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start Deleting Tier ==========')
        context = super(TierDeleteView, self).get_context_data(**kwargs)
        tier_id = context['fee_tier_id']
        self.logger.info('Start Getting Tier detail')
        tier_to_delete = self._get_tier_detail(tier_id)
        for i in tier_to_delete:
            if tier_to_delete[i] is None:
                tier_to_delete[i] = 'Non'
        context['delete_tier'] = tier_to_delete
        context['command'] = kwargs.get('command')
        service_detail, success = self._get_service_detail(context['service_id'])
        command_name, success = self._get_command_name(context['command_id'])

        context.update({
            'service_name': service_detail.get('service_name', 'unknown'),
            'command_name': command_name,
        })
        self.logger.info('Finish Getting Tier detail')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(TierDeleteView, self).get_context_data(**kwargs)
        tier_id = kwargs.get('fee_tier_id')
        command_id = context['command_id']
        service_id = context['service_id']
        service_command_id = context['service_command_id']
        data, success = self._delete_tier(tier_id)
        self.logger.info('========== Finish Deleting Tier ==========')
        if success:
            request.session['delete_tier_msg'] = 'Deleted data successfully'
        else:
            request.session['delete_tier_msg'] = data

        return redirect('services:fee_tier_list', service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id)


    def _delete_tier(self, fee_tier_id):
        return self._delete_method(api_path=api_settings.TIER_PATH.format(fee_tier_id),
                                   func_description="Delete Tier",
                                   logger=logger)
