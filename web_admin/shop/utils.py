from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin import api_settings, settings
from authentications.apps import InvalidAccessToken




def get_all_shop_type(self):
    self.logger.info('========== Start get all shop type ==========')
    api_path = api_settings.GET_LIST_SHOP_TYPE
    params = {'paging': False}
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=params
    )

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_types', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params=params)
    self.logger.info('========== Finish get all shop type ==========')
    return [i for i in data.get('shop_types', []) if not i.get('is_deleted')]

def get_all_shop_category(self):
    api_path = api_settings.GET_LIST_SHOP_CATEGORIES
    params = {'paging': False}
    self.logger.info('========== Start get all shop category ==========')
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=params
    )

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_categories', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params=params)
    self.logger.info('========== Finish get all shop category ==========')
    return [i for i in  data.get('shop_categories', []) if not i.get('is_deleted')]

def get_system_country(self):
    self.logger.info('========== Start get country code ==========')
    is_success, status_code, data = RestFulClient.get(
                                        url=api_settings.ADD_COUNTRY_CODE_URL,
                                        headers=self._get_headers(),
                                        loggers=self.logger
                                        )
    if data is None:
        data = {}
    API_Logger.get_logging(loggers=self.logger, params={}, response=data, status_code=status_code)
    self.logger.info('========== Finish get country code ==========')

    return data['value']

def get_agent_supported_channels(self):
    self.logger.info('========== Start get supported channel for agent ==========')
    api_path = api_settings.SEARCH_CHANNEL
    body = {}
    body['user_type_id'] = 2
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body
    )

    data = data.get('channels', [])
    API_Logger.post_logging(loggers=self.logger,
                            response=data,
                            status_code=status_code,
                            is_getting_list=True,
                            params=body)
    self.logger.info('========== Finish get supported channel for agent ==========')
    return data

def get_channel_permissions_list(self, shopId):
    self.logger.info('========== Start get channel access permission for the shop ==========')
    api_path = api_settings.SEARCH_CHANNEL_PERMISSION
    body = {}
    body['shop_id'] = shopId
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body
    )

    data = data.get('permissions', [])
    API_Logger.post_logging(loggers=self.logger,
                            response=data,
                            status_code=status_code,
                            is_getting_list=True,
                            params=body)
    self.logger.info('========== Finish get channel access permission for the shop ==========')
    return data

def get_devices_list(self, shopId):
    self.logger.info('========== Start get all devices under the shop ==========')
    api_path = api_settings.SEARCH_AGENT_DEVICES
    body = {}
    body['shop_id'] = shopId
    body['is_deleted'] = False
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body
    )

    data = data.get('devices', [])
    API_Logger.post_logging(loggers=self.logger,
                            response=data,
                            status_code=status_code,
                            is_getting_list=True,
                            params=body)
    self.logger.info('========== Finish get all devices under the shop ==========')
    return data

def check_permission_device_management(self):
    permissions = {}
    permissions['CAN_BLOCK_AGENT_CHANNELS'] = self.check_membership(['CAN_BLOCK_AGENT_CHANNELS'])
    permissions['CAN_EDIT_AGENT_CHANNEL_DETAILS'] = self.check_membership(['CAN_EDIT_AGENT_CHANNEL_DETAILS'])
    permissions['CAN_UNBIND_AGENT_DEVICE'] = self.check_membership(['CAN_UNBIND_AGENT_DEVICE'])
    permissions['CAN_DISABLE_AGENT_DEVICE'] = self.check_membership(['CAN_DISABLE_AGENT_DEVICE'])
    return permissions

def get_channel_detail(self, channel_id):
    self.logger.info('========== Start get channel detail ==========')
    api_path = api_settings.SEARCH_CHANNEL
    body = {}
    body['id'] = channel_id
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body
    )

    data = data.get('channels', [])
    API_Logger.post_logging(loggers=self.logger,
                            response=data,
                            status_code=status_code,
                            is_getting_list=False,
                            params=body)
    self.logger.info('========== Finish get channel detail ==========')
    return data[0]

def get_shop_details(self, shop_id):
    url = api_settings.GET_DETAIL_SHOP
    body = {
        "id": shop_id
    }
    self.logger.info('========== Start get shop detail ==========')
    success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                       headers=self._get_headers(),
                                                                       loggers=self.logger,
                                                                       params=body,
                                                                       timeout=settings.GLOBAL_TIMEOUT)
    if data is None:
        data = {}
    else:
        data = data['shops'][0]

    API_Logger.post_logging(loggers=self.logger, params=body,response=data,
                            status_code=status_code, is_getting_list=False)
    self.logger.info('========== Finish get shop detail ==========')
    # TODO
    return data


def convert_shop_to_form(shop):
    form = {}
    form["id"] = str(shop["id"])
    form["agent_id"] = str(shop["agent_id"]) if shop["agent_id"] else ""
    form["acquisition_source"] = shop["acquisition_source"]
    form["name"] = shop["name"]
    if shop["shop_type"]:
        form["shop_type_id"] = str(shop["shop_type"]["id"]) if shop["shop_type"]["id"] else ""
        form["shop_type_name"] = shop["shop_type"]["name"]
    if shop["shop_category"]:
        form["shop_category_id"] = str(shop["shop_category"]["id"]) if shop["shop_category"]["id"] else ""
        form["shop_category_name"] = shop["shop_category"]["name"]
    form["country"] = shop["address"]["country"]
    form["postal_code"] = shop["postal_code"]
    form["province"] = shop["address"]["province"]
    form["city"] = shop["address"]["city"]
    form["district"] = shop["address"]["district"]
    form["commune"] = shop["address"]["commune"]
    form["address"] = shop["address"]["address"]
    form["landmark"] = shop["address"]["landmark"]
    form["latitude"] = shop["address"]["latitude"]
    form["longitude"] = shop["address"]["longitude"]
    form["representative_first_name"] = shop["representative_first_name"]
    form["representative_middle_name"] = shop["representative_middle_name"]
    form["representative_last_name"] = shop["representative_last_name"]
    form["representative_mobile_number"] = shop["representative_mobile_number"]
    form["representative_telephone_number"] = shop["representative_telephone_number"]
    form["representative_email"] = shop["representative_email"]
    form["shop_mobile_number"] = shop["shop_mobile_number"]
    form["shop_telephone_number"] = shop["shop_telephone_number"]
    form["shop_email"] = shop["shop_email"]
    form["relationship_manager_id"] = shop["relationship_manager_id"]
    form["relationship_manager_name"] = shop["relationship_manager_name"]
    form["relationship_manager_email"] = shop["relationship_manager_email"]
    form["acquiring_sales_executive_name"] = shop["acquiring_sales_executive_name"]
    form["sales_region"] = shop["sales_region"]
    form["account_manager_name"] = shop["account_manager_name"]
    form["ref1"] = shop["ref1"]
    form["ref2"] = shop["ref2"]
    return form


def convert_form_to_shop(form):
    address = {}
    address["address"] = form["address"]
    address["city"] = form["city"]
    address["province"] = form["province"]
    address["district"] = form["district"]
    address["commune"] = form["commune"]
    address["country"] = form["country"]
    address["landmark"] = form["landmark"]
    address["latitude"] = form["latitude"]
    address["longitude"] = form["longitude"]

    shop = {}
    shop["agent_id"] = int(form["agent_id"]) if form.get("agent_id", None) else None
    shop["shop_type_id"] = int(form["shop_type_id"]) if form.get("shop_type_id", None) else None
    shop["name"] = form["name"]
    shop["shop_category_id"] = int(form["shop_category_id"]) if form.get("shop_category_id", None) else None
    shop["address"] = address
    shop["relationship_manager_id"] = form["relationship_manager_id"]
    shop["acquisition_source"] = form["acquisition_source"]
    shop["postal_code"] = form["postal_code"]
    shop["representative_first_name"] = form["representative_first_name"]
    shop["representative_middle_name"] = form["representative_middle_name"]
    shop["representative_last_name"] = form["representative_last_name"]
    shop["representative_mobile_number"] = form["representative_mobile_number"]
    shop["representative_telephone_number"] = form["representative_telephone_number"]
    shop["representative_email"] = form["representative_email"]
    shop["shop_mobile_number"] = form["shop_mobile_number"]
    shop["shop_telephone_number"] = form["shop_telephone_number"]
    shop["shop_email"] = form["shop_email"]
    shop["relationship_manager_name"] = form["relationship_manager_name"]
    shop["relationship_manager_email"] = form["relationship_manager_email"]
    shop["acquiring_sales_executive_name"] = form["acquiring_sales_executive_name"]
    shop["sales_region"] = form["sales_region"]
    shop["account_manager_name"] = form["account_manager_name"]
    shop["ref1"] = form["ref1"]
    shop["ref2"] = form["ref2"]
    return shop


def get_agent_detail(self, id):
    api_path = api_settings.AGENT_DETAIL_PATH
    params = {'id': id}
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=params
    )
    if success:
        return data['agents'][0]
    elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
        raise InvalidAccessToken(status_message)


def search_shop(self, params):
    self.logger.info('========== Start searching shop ==========')
    api_path = api_settings.SEARCH_SHOP
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=params
    )

    data = data or {}
    page = data.get("page", {})
    self.logger.info(
        'Total element: {}'.format(page.get('total_elements', 0)))
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shops', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params=params)
    self.logger.info('========== Finish searching shop ==========')
    return data