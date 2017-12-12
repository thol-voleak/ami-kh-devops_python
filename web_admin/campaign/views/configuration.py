from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import JsonResponse
from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods
import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from campaign.models import terms_mapping
logger = logging.getLogger(__name__)


class MappingView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "campaign/configuration.html"
    logger = logger

    group_required = "CAN_EDIT_CAMPAIGN_CONFIGURATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(MappingView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        terms = list(terms_mapping.objects.all())
        return render(request, self.template_name, {'data': terms})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating service ==========')
        term = request.POST.get('term')
        description = request.POST.get('description')

        the_term = terms_mapping.objects.get(term=term)
        if the_term:
            the_term.description = description
            the_term.updated_by = request.user.username
            the_term.save()
            the_term = terms_mapping.objects.get(term=term)  # get it back
            if the_term:
                return JsonResponse({"status": 2, "msg": "Updated data successfully"})
            else:
                return JsonResponse({"status": 3, "msg": "The term \"{}\" is not found".format(term)})

        else:
            return JsonResponse({"status": 3, "msg": "The term \"{}\" is not found".format(term)})




