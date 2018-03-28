from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin import api_settings


def get_all_shop_type(self):
    api_path = api_settings.GET_LIST_SHOP_TYPE
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger)

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_types', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params={'paging': False, 'is_deleted': False})
    return data.get('shop_types', [])

def get_all_shop_category(self):
    api_path = api_settings.GET_LIST_SHOP_CATEGORIES
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger)

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_categories', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params={'paging': False, 'is_deleted': False})
    return data.get('shop_categories', [])


def get_system_country(self):
    # TODO
    return "VN"


def get_shop_details(self, id):
    # TODO
    return {
        "id": 0,
        "agent_id": 0,
        "shop_type": {
          "id": "string",
          "name": "string"
        },
        "shop_category": {
          "id": "string",
          "name": "string"
        },
        "name": "string",
        "address": {
          "address": "string",
          "city": "string",
          "province": "string",
          "district": "string",
          "commune": "string",
          "country": "string",
          "landmark": "string",
          "latitude": "string",
          "longitude": "string"
        },
        "relationship_manager_id": "string",
        "acquisition_source": "string",
        "postal_code": "string",
        "representative_first_name": "string",
        "representative_middle_name": "string",
        "representative_last_name": "string",
        "representative_mobile_number": "string",
        "representative_telephone_number": "string",
        "representative_email": "string",
        "shop_mobile_number": "string",
        "shop_telephone_number": "string",
        "shop_email": "string",
        "relationship_manager_name": "string",
        "relationship_manager_email": "string",
        "acquiring_sales_executive_name": "string",
        "sales_region": "string",
        "account_manager_name": "string",
        "is_deleted": True,
        "created_timestamp": "2018-03-23T06:23:26.176Z",
        "last_updated_timestamp": "2018-03-23T06:23:26.176Z"
    }


def convert_shop_to_form(shop):
    form = {}
    form["id"] = shop["id"]
    form["agent_id"] = shop["agent_id"]
    form["acquisition_source"] = shop["acquisition_source"]
    form["name"] = shop["name"]
    form["shop_type_id"] = shop["shop_type"]["id"]
    form["shop_category_id"] = shop["shop_category"]["id"]
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
    # form["reference_1"] = shop["reference_1"]
    # form["reference_2"] = shop["reference_2"]
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
    shop["agent_id"] = form["agent_id"]
    shop["shop_type_id"] = form["shop_type_id"]
    shop["name"] = form["name"]
    shop["shop_category_id"] = form["shop_category_id"]
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
    # shop["reference_1"] = form["reference_1"]
    # shop["reference_2"] = form["reference_2"]
    return shop


def get_agent_detail(id):
    # TODO
    return {
        "id": id,
        "agent_type_id": 0,
        "parent_id": 0,
        "grand_parent_id": 0,
        "last_name": "last_name",
        "firstname": "firstname",
        "date_of_birth": "2018-03-23T06:03:44.634Z",
        "gender": "string",
        "national": "string",
        "primary_identify_id": "string",
        "primary_identify_type": "string",
        "primary_place_of_issue": "string",
        "primary_issue_date": "2018-03-23T06:03:44.634Z",
        "primary_expire_date": "2018-03-23T06:03:44.634Z",
        "nationality": "string",
        "country": "string",
        "province": "string",
        "city": "string",
        "district": "string",
        "commune": "string",
        "address": "string",
        "landmark": "string",
        "longitude": "string",
        "latitude": "string",
        "permanent_country": "string",
        "permanent_province": "string",
        "permanent_city": "string",
        "permanent_district": "string",
        "permanent_commune": "string",
        "permanent_address": "string",
        "permanent_landmark": "string",
        "permanent_longitude": "string",
        "permanent_latitude": "string",
        "email": "email",
        "kyc_status": True,
        "kyc_remark": "string",
        "kyc_level": "string",
        "kyc_updated_timestamp": "2018-03-23T06:03:44.634Z",
        "primary_mobile_number": "primary_mobile_number",
        "secondary_mobile_number": "string",
        "tertiary_mobile_number": "string",
        "unique_reference": "string",
        "bank": {
          "name": "string",
          "branch_city": "string",
          "branch_area": "string",
          "account_number": "string"
        },
        "contract": {
          "type": "string",
          "number": 0,
          "sign_date": "string",
          "issue_date": "string",
          "expired_date": "string",
          "extended_type": "string",
          "day_of_period_reconciliation": "string"
        }
    }
