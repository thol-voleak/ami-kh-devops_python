from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper


def get_label_levels(request):
    success, status_code, message, data = RestfulHelper.send(
        method='GET',
        url=api_settings.TIER_LEVELS_LIST,
        params={},
        request=request,
        description='getting label levels list',
        log_count_field='data'
    )
    if success:
        request.session['tier_levels'] = data
        return data
    return {}