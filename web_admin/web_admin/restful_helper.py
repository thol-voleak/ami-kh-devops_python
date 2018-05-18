from authentications.apps import InvalidAccessToken
from authentications.models import Authentications
from web_admin import RestFulClient
from web_admin.utils import build_logger, build_auth_header_from_request


class RestfulHelper:
    @classmethod
    def send(cls, method, url, params, request, description=None, log_count_field=None):
        loggers = build_logger(request, __name__)

        if description:
            loggers.info("===== Start {} =====".format(description))

        headers = build_auth_header_from_request(request)

        if len(params) > 0:
            loggers.info("Request data: {} ".format(params))

        if method == 'GET':
            is_success, status_code, data = RestFulClient.get(url, loggers, headers)
            status_message = None
        elif method == 'POST':
            is_success, status_code, status_message, data = RestFulClient.post(url, headers, loggers, params)
        elif method == 'PUT':
            is_success, status_code, status_message, data = RestFulClient.put(url, headers, loggers, params)
        elif method == 'DELETE':
            is_success, status_code, status_message = RestFulClient.delete(url, headers, loggers, params)
            data = None

        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            raise InvalidAccessToken(status_message)

        if log_count_field:
            log_data = data
            for field in log_count_field.split('.'):
                if field == "data":
                    continue
                log_data = log_data.get(field, {})

            count = len(log_data)
            loggers.info('Response count: {}'.format(count))
        else:
            loggers.info('Response data: {}'.format(data))

        if description:
            loggers.info("===== Finish {} =====".format(description))

        return is_success, status_code, status_message, data