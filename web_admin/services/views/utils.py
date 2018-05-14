from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper


def get_payment_decimal(request):
    success, status_code, message, data = RestfulHelper.send(
        method='GET',
        url=api_settings.PAYMENT_DECIMAL,
        params={},
        request=request,
        description='getting payment decimal',
    )

    return data