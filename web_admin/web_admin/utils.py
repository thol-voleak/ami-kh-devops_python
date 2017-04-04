import datetime

def format_date_time(data):
    for item in data:
        if (item['created_timestamp'] is not None) and (item['created_timestamp'] != "null"):
            created_at = item['created_timestamp'] / 1000.0
            item['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')

        if (item['last_updated_timestamp'] is not None) and (
                    item['last_updated_timestamp'] != "null"):
            created_at = item['last_updated_timestamp'] / 1000.0
            item['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')
    return data