from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper

def get_service_list(self, params):
    api_path = api_settings.GET_CHANNEL_SERVICE

    success, status_code, status_message, data = RestfulHelper.send("POST", api_path, params, self.request, "get service list", "data.services")
    if success:
        return data['services']
    else:
        return []

def get_api_detail(self, api_id):
    url = api_settings.GET_CHANNEL_API
    params = {
        "id": api_id
    }
    is_success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request,
                                                                       "get api detail")
    if is_success:
        data = data["apis"][0]
        if 'service' in data:
            data['service_id'] = data['service']['id']
        if 'is_required_access_token' in data:
            if data['is_required_access_token'] == True:
                data['require_access_token'] = "1"
            else:
                data['require_access_token'] = "0"
        return data
    else:
        return {}

def get_api_list(self, params):
    api_path = api_settings.GET_CHANNEL_API

    success, status_code, status_message, data = RestfulHelper.send("POST", api_path, params, self.request, "get api channel list", "data.apis")
    if data is None:
        data = {}
        data['apis'] = []
    return data