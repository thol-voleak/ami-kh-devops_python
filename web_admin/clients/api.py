import json
import logging
import requests
import time

from django.conf import settings
from django.http import HttpResponse

from authentications.models import Authentications

logger = logging.getLogger(__name__)


def delete_client_by_id(request, client_id):
    logger.info("========== Start delete client id ==========")
    if request.method == "POST":
        url = settings.DELETE_CLIENT_URL.format(client_id)
        auth = Authentications.objects.get(user=request.user)
        access_token = auth.access_token

        headers = {
            'content-type': 'application/json',
            'correlation-id': "xxxxx",
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        start_date = time.time()
        response = requests.delete(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for delete {} client id is {} sec.".format(client_id, done - start_date))
        logger.info("Response for delete {} client id is {}".format(client_id, response.content))

        json_response = response.json()
        logger.info("========== Finished deleted client id ==========")
        if response.status_code == 200:
            return HttpResponse(json.dumps(json_response["status"]), content_type="application/json")

        raise Exception("{}".format(json_data["message"]))
