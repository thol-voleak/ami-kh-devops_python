import json
import logging
import requests
import time
import random
import string

from django.conf import settings
from django.http import HttpResponse

from authentications.models import Authentications

logger = logging.getLogger(__name__)


class ClientApi():
    def regenerate(request, client_id):
        logger.info('========== Start regenerating client secret ==========')

        url = settings.REGENERATE_CLIENT_SECRET_URL.format(client_id)
        auth = Authentications.objects.get(user=request.user)
        access_token = auth.access_token

        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        start_date = time.time()
        response = requests.post(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for regenerate client secret for {} client id is {} sec.".format(client_id,
                                                                                                    done - start_date))

        response_json = response.json()
        status = response_json['status']
        if status['code'] == "success":
            logger.info("Client secret was regenerated.")
            logger.info('========== Finish regenerate client secret ==========')
            return HttpResponse(status=200, content=response)
        else:
            logger.info("Error regenerate client secret.")
            logger.info('========== Finish regenerate client secret ==========')
            return HttpResponse(status=500, content=response)

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
