from django.views.generic.base import TemplateView
from web_admin.utils import build_logger
from django.shortcuts import render, redirect
from web_admin.restful_helper import RestfulHelper
from .utils import get_label_levels
from web_admin import api_settings
from django.contrib import messages
import logging


logger = logging.getLogger(__name__)


class TierLevelEdit(TemplateView):
    template_name = "services/tier_levels/edit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(request, __name__)
        return super(TierLevelEdit, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TierLevelEdit, self).get_context_data(**kwargs)
        lvl_id = kwargs.get('level_id')
        label_level = self.get_label_detail(int(lvl_id))

        context['form'] = label_level
        return context

    def post(self, request, *args, **kwargs):
        context = super(TierLevelEdit, self).get_context_data(**kwargs)
        lvl_id = kwargs.get('level_id')
        form = request.POST

        success, status_code, message, data = RestfulHelper.send(
            method='PUT',
            url=api_settings.TIER_LEVELS_EDIT.format(tier_level_id=lvl_id),
            params={'label': form['label']},
            request=request,
            description='updating label level',
        )

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Label successfully updated'
            )
            return redirect('services:tier_label_list')
        else:
            context['form'] = form
            messages.add_message(
                request,
                messages.ERROR,
                message
            )
            return render(request, self.template_name, context=context)

    def get_label_detail(self, lvl_id):
        label_levels = self.request.session.get('tier_levels')
        if not label_levels:
            label_levels = get_label_levels(self.request)

        for lvl in label_levels:
            if lvl.get('id') == lvl_id:
                return lvl
        return {}