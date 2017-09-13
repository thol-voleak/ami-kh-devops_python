from authentications.apps import InvalidAccessToken
from web_admin import api_settings, RestFulClient


class BanksClient:
    @classmethod
    def create_bank(cls, headers, params, logger):
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.SEARCH_CARD_SOF_PATH, headers=headers, loggers=logger, params=params
        )

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message, data

    @classmethod
    def get_bank_details(cls, params, headers, logger):
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_BANK_PROFILE_REPORT_PATH, headers=headers, loggers=logger, params=params
        )

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        if is_success and len(data) > 0:
            bank_detail = data[0]

        return is_success, status_code, status_message, bank_detail

    @classmethod
    def get_currencies_list(cls, header, logger):
        logger.info("Stating to get all currency from backend.")
        url = api_settings.GET_ALL_CURRENCY_URL
        is_success, status_code, data = RestFulClient.get(url=url, headers=header, loggers=logger)

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                return is_success, status_code, data

        if is_success:
            value = data.get('value', None)
            if value is not None:
                currencies = [i.split('|') for i in value.split(',')]
            else:
                currencies = data
        return is_success, status_code, currencies
