from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class DetailView(TemplateView):

    template_name = "channel-gateway-service/detail.html"