from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin import api_settings, setup_logger

def get_agent_type_by_agent_id(self, id):
    api_path = api_settings.AGENT_DETAIL_PATH

    body = {
        "id": id,
    }

    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body)
    API_Logger.post_logging(loggers=self.logger, params=body,
                            response=data.get('agents', []),
                            status_code=status_code, is_getting_list=True)
    data = data or {}
    if data.get('agents'):
        return data.get('agents')[0]['agent_type_id']

def _create_product_relation(self, agent_id):
    # get all applicable products
    self.logger.info('========== Start getting agent type ==========')
    agent_type = get_agent_type_by_agent_id(self, agent_id)
    self.logger.info('========== Finish getting agent type ==========')
    if isinstance(agent_type, int):
        self.logger.info('========== Start getting all applicable product by agent type ==========')
        applicable_products_of_agent = get_products_by_agent_type(self, agent_type)
        self.logger.info('========== Finish getting all applicable product by agent type ==========')

        self.logger.info('========== Start getting applied product by agent type  ==========')
        checked_products_of_agent = get_products_by_agent(self, agent_id)
        self.logger.info('========== Finish getting applied product by agent type ==========')

        # get all products to get product name
        self.logger.info('========== Start getting all products  ==========')
        all_products = get_all_products(self)
        self.logger.info('========== Finish getting all products ==========')

        # get all categories to get category name
        self.logger.info('========== Start getting all categories  ==========')
        all_categories = get_all_categories(self)
        self.logger.info('========== Finish getting all categories  ==========')

    applicable_product = []
    for atp in applicable_products_of_agent:
        for p in all_products:
            if atp['product_id'] != p['id']:
                continue
            atp['product_name'] = p['name']

            for c in all_categories:
                if p['category_id'] != c['id']:
                    continue
                if c['is_deleted']:
                    break
                atp['category_name'] = c['name']
                applicable_product.append(atp)
                break
            break

    checked_id = [i['product_id'] for i in checked_products_of_agent]

    applicable_categories = {}
    for p in applicable_product:
        # verify if applicable product is applied
        if p['product_id'] not in checked_id:
            p['is_checked'] = False
        else:
            p['is_checked'] = True

        # categorize products
        if p['category_name'] not in applicable_categories:
            applicable_categories[p['category_name']] = []
        else:
            applicable_categories[p['category_name']].append(p)

    return applicable_categories

def get_products_by_agent(self, id):
    api_path = api_settings.GET_PRODUCT_AGENT_RELATION

    body = {
        "agent_id": id,
    }

    success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                    headers=self._get_headers(),
                                                                    loggers=self.logger,
                                                                    params=body)
    API_Logger.post_logging(loggers=self.logger, params=body,
                            response=data.get('relations', []),
                            status_code=status_code, is_getting_list=True)
    data = data or {}
    return data.get('relations', [])

def get_products_by_agent_type(self, id):
    api_path = api_settings.PRODUCT_AGENT_TYPE

    body = {
        "agent_type_id": id,
    }

    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger,
        params=body)

    API_Logger.post_logging(loggers=self.logger, params=body,
                            response=data.get('relations', []),
                            status_code=status_code, is_getting_list=True)
    data = data or {}

    return data.get('relations', [])

def get_all_products(self):
    api_path = api_settings.GET_PRODUCTS

    body = {
        "paging": False,
        "is_deleted": False,
        "is_active": True
    }

    success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                    headers=self._get_headers(),
                                                                    loggers=self.logger,
                                                                    params=body)
    API_Logger.post_logging(loggers=self.logger, params=body,
                            response=data.get('products', []),
                            status_code=status_code, is_getting_list=True)
    data = data or {}
    return data.get('products', [])

def get_all_categories(self):
    api_path = api_settings.GET_CATEGORIES

    body = {
        "paging": False,
        "is_active": True
    }

    success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                    headers=self._get_headers(),
                                                                    loggers=self.logger,
                                                                    params=body)
    API_Logger.post_logging(loggers=self.logger, params=body,
                            response=data.get('categories', []),
                            status_code=status_code, is_getting_list=True)
    data = data or {}

    return data.get('categories', [])