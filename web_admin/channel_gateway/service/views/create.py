from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView):

    template_name = "channel-gateway-service/create.html"