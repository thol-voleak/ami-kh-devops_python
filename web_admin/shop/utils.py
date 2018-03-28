def get_all_shop_type():
    # TODO
    list = [
        {
            "id": 1,
            "name": "1"
        },
        {
            "id": 2,
            "name": "2"
        }
    ]

    return list


def get_all_shop_category():
    # TODO
    list = [
        {
            "id": 1,
            "name": "1"
        },
        {
            "id": 2,
            "name": "2"
        }
    ]

    return list


def get_system_country():
    # TODO
    return "VN"


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
