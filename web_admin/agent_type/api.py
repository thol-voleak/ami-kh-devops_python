import logging
import time

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ClientApi():
    def delete_agent_type_by_id(request, agent_type_id):

        logger.info("========== Start deleting agent type ==========")
        logger.info('Agent Type ID to be deleted: {}'.format(agent_type_id))
        if request.method == "POST":
            url = settings.DELETE_AGENT_TYPE_URL.format(agent_type_id)

            start_date = time.time()
            response = requests.delete(url, headers=get_auth_header(request.user),
                                       verify=settings.CERT)
            done = time.time()
            logger.info("Response time for delete {} agent type id is {} sec.".format(agent_type_id, done - start_date))
            logger.info("Response for delete {} agent type id is {}".format(agent_type_id, response.content))

            response_json = response.json()
            status = response_json['status']

            logger.info("Response Code is {}".format(status['code']))

            if response.status_code == 200:
                if status['code'] == "success":
                    logger.info("Agent Type was deleted.")
                    logger.info("========== Finished deleting agent type id ==========")
                    return HttpResponseRedirect(reverse('agent_type:agent-type-list', args=(None)))
                else:
                    logger.info("Error deleting agent type {}".format(agent_type_id))
                    logger.info("========== Finished deleting agent type id ==========")
                    return HttpResponse(status=500, content=response)
            else:
                logger.info("Error deleting agent type {}".format(agent_type_id))
                logger.info("Status code {}".format(response.status_code))

                logger.info('========== Finish suspending client ==========')
                return HttpResponse(status=response.status_code, content=response)

            raise Exception("{}".format(response_json["status"]["message"]))
        else:
            logger.info('Invalid HTTP Method')
            logger.info("========== Finish deleting agent type ==========")
