from authentications.apps import InvalidAccessToken

class API_Logger:
    @classmethod
    def get_logging(self, loggers=None, params={}, response=[], status_code=""):
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            raise InvalidAccessToken("")

        # Filter sensitive data
        params = API_Logger._filter_sensitive_fields(params=params)

        if len(params) > 0:
            loggers.info("Params: {} ".format(params))

        response = response or []

        if (type(response) is list) and (len(response) > 1):
            loggers.info('Response_content_count: {}'.format(len(response)))
        else:
            loggers.info('Response_content: {}'.format(response))


    @classmethod
    def put_logging(self, loggers=None, params={}, response={}, status_code=""):
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            raise InvalidAccessToken("")

        # Filter sensitive data
        params = API_Logger._filter_sensitive_fields(params=params)

        if len(params) > 0:
            loggers.info("Params: {} ".format(params))

        response = response or {}

        if (type(response) is list) and (len(response) > 1):
            loggers.info('Response_content_count: {}'.format(len(response)))
        else:
            loggers.info('Response_content: {}'.format(response))


    @classmethod
    def post_logging(self, loggers=None, params={}, response={}, status_code=""):
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            raise InvalidAccessToken("")

        # Filter sensitive data
        params = API_Logger._filter_sensitive_fields(params=params)

        if len(params) > 0:
            loggers.info("Params: {} ".format(params))

        response = response or {}
        if (type(response) is list) and (len(response) > 1):
            loggers.info('Response_content_count: {}'.format(len(response)))
        else:
            loggers.info('Response_content: {}'.format(response))


    @classmethod
    def delete_logging(self, loggers=None, params={}, response={}, status_code=""):
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            raise InvalidAccessToken("")

        # Filter sensitive data
        params = API_Logger._filter_sensitive_fields(params=params)

        if len(params) > 0:
            loggers.info("Params: {} ".format(params))

        response = response or {}
        if (type(response) is list) and (len(response) > 1):
            loggers.info('Response_content_count: {}'.format(len(response)))
        else:
            loggers.info('Response_content: {}'.format(response))


    @staticmethod
    def _filter_sensitive_fields(params={}):

        if 'password' in params:
            params['password'] = '******'

        if 're-password' in params:
            params['re-password'] = '******'

        return params;