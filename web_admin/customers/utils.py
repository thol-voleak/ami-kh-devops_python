from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin import api_settings

def check_permission_customer_management(self):
    permissions = {}
    permissions['CAN_VIEW_CUSTOMER_MANAGEMENT'] = self.check_membership(['CAN_VIEW_CUSTOMER_MANAGEMENT'])
    permissions['CAN_ACCESS_CUSTOMER_DEVICE_TAB'] = self.check_membership(['CAN_ACCESS_CUSTOMER_DEVICE_TAB'])
    permissions['CAN_BLOCK_CUSTOMER_CHANNELS'] = self.check_membership(['CAN_BLOCK_CUSTOMER_CHANNELS'])
    permissions['CAN_EDIT_CUSTOMER_CHANNEL_DETAILS'] = self.check_membership(['CAN_EDIT_CUSTOMER_CHANNEL_DETAILS'])
    permissions['CAN_UNBIND_CUSTOMER_DEVICE'] = self.check_membership(['CAN_UNBIND_CUSTOMER_DEVICE'])
    permissions['CAN_DISABLE_CUSTOMER_DEVICE'] = self.check_membership(['CAN_DISABLE_CUSTOMER_DEVICE'])
    return permissions

def get_supported_channels(self):
    self.logger.info('========== Start get channel for customer ==========')
    api_path = api_settings.CUSTOMER_CHANNEL_LIST_URL
    body = {}
    body['user_type_id'] = 1
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
    self.logger.info('========== Finish get channel for customer ==========')
    return data

def get_channel_permissions_list(self, customerId):
    self.logger.info('========== Start get channel access permission for customer ==========')
    api_path = api_settings.CUSTOMER_CHANNEL_PERMISSION_LIST_URL
    body = {}
    body['user_id'] = customerId
    body['user_type_id'] = 1
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
    self.logger.info('========== Finish get channel access permission for customer ==========')
    return data