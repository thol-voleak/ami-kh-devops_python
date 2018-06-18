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


def get_currency_by_service_id(request, service_id):
    currency = request.session.get('{}_currency'.format(service_id))
    if currency:
        return currency

    success, status_code, message, data = RestfulHelper.send(
        method='GET',
        url=api_settings.SERVICE_DETAIL_URL.format(service_id),
        params={},
        request=request,
        description='getting service currency',
    )

    currency = data.get('currency') if data else ''
    request.session['{}_currency'.format(service_id)] = currency
    return currency