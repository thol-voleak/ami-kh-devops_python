from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper

def get_service_list(self, params):
    api_path = api_settings.GET_CHANNEL_SERVICE

    success, status_code, status_message, data = RestfulHelper.send("POST", api_path, params, self.request, "get service list", "data.services")
    if data is None:
        data = {}
        data['services'] = []
    return data