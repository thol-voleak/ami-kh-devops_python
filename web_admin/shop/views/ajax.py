from django.core import serializers
from django.http import HttpResponse, JsonResponse

from shop.utils import get_agent_detail


def agent_detail(request, id):
    agent = get_agent_detail(id)
    return JsonResponse(agent)
