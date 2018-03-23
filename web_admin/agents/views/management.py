from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.api_logger import API_Logger
from web_admin.api_settings import SEARCH_RELATIONSHIP, RELATIONSHIP_TYPES_LIST
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentManagement(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "agents/management.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagement, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagement, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(AgentManagement, self).get_context_data(**kwargs)
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        default_tab = 0
        if not permissions['CAN_ACCESS_SUMMARY_TAB']:
            default_tab = 1
        relationship_type_id = []
        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions,
             'relationship_types': self._get_relationship_types(),
             'relationship_type_id':relationship_type_id,
             'default_tab': default_tab
             })

        if permissions['CAN_ACCESS_RELATIONSHIP_TAB']:
            self.logger.info('========== Start getting Relationships list ==========')
            data, success, status_message = self._get_relationships(params=body)
            if success:
                relationships_list = data.get("relationships", [])
                summary_relationships = list(relationships_list)
                if len(relationships_list) > 10:
                    summary_relationships = relationships_list[:10]

                page = data.get("page", {})
                context.update(
                    {'search_count': page.get('total_elements', 0),
                     'relationships': relationships_list,
                     'summary_relationships': summary_relationships,
                     'relationship_list_length': len(relationships_list)
                     })

            self.logger.info('========== Finish getting Relationships list ==========')
        self.logger.info('========== Start getting product portfolio ==========')

        agent_type = self.get_agent_type_by_agent_id(int(context['agent_id']))
        if isinstance(agent_type, int):
            applicable_products_of_agent = self.get_products_by_agent_type(agent_type)
            checked_products_of_agent = self.get_products_by_agent(int(context['agent_id']))

            # get all products to get product name
            all_products = self.get_all_products()

            # get all categories to get category name
            all_catelogies = self.get_all_categories()

            applicable_categories = self._create_product_relation(checked_products_of_agent, applicable_products_of_agent, all_products, all_catelogies)
            context.update({
                'applicable_categories': applicable_categories,
            })
        self.logger.info('========== Finish getting product portfolio ==========')
        return render(request, self.template_name, context)

    def _create_product_relation(self, checked_products_of_agent, applicable_products_of_agent, all_products, all_categories):
        # get all applicable products
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

    def _get_relationships(self, params):

        api_path = SEARCH_RELATIONSHIP
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=params, response=data.get('relationships', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message
    def _get_relationship_types(self):
        self.logger.info('========== Start getting relationship types ==========')
        is_success, status_code, data = RestFulClient.get(
            url=RELATIONSHIP_TYPES_LIST,
            headers=self._get_headers(),
            loggers=self.logger)
        if is_success:
            self.logger.info('Response_content: {}'.format(data))
            self.logger.info('========== finish get relationship types ==========')
            for i in data:
                if i['name'] == 'FL-Agent':
                    i['name'] = 'Frontline-Agent'
            return data
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def post(self, request, *args, **kwargs):
        params = {}
        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        relationship_types = self._get_relationship_types()
        self.logger.info('========== start getting relationship ==========')
        agent_id = int(kwargs.get('agent_id'))
        list_relationship_type = request.POST.getlist('list_relationship_type')
        partner_role = request.POST.get('partner_role')
        relationship_partner_id = request.POST.get('relationship_partner_id')
        # params['paging'] = False
        # params['page_index'] = 0
        if list_relationship_type:
            list_relationship_type = [int(i) for i in list_relationship_type]
            params['relationship_type_ids'] = list_relationship_type
        if relationship_partner_id:
            relationship_partner_id = int(relationship_partner_id)
            if partner_role == '0':
                params['user_id'] = agent_id
            elif partner_role == '1':
                params['main_user_id'] = relationship_partner_id
                params['sub_user_id'] = agent_id
            elif partner_role == '2':
                params['main_user_id'] = agent_id
                params['sub_user_id'] = relationship_partner_id
        else:
            params['user_id'] = agent_id

        self.logger.info("Params: {} ".format(params))
        data, success, status_message = self._get_relationships(params=params)



        summary_relationship_count = request.POST.get('count_summary_relationship')
        relationship_count = request.POST.get('count_relationship')
        if relationship_count:
            relationship_count = int(relationship_count)
        summary_relationships = []
        if summary_relationship_count:
            for i in range(0, int(summary_relationship_count)):
                relationship_type = request.POST.get('relationship_type_' + str(i))
                main_id = request.POST.get('main_user_id_' + str(i))
                sub_id = request.POST.get('sub_user_id_' + str(i))
                created_date = request.POST.get('created_date_' + str(i))
                modified_date = request.POST.get('modified_date_' + str(i))
                main_first_name = request.POST.get('main_user_first_name_' + str(i))
                main_last_name = request.POST.get('main_user_last_name_' + str(i))
                sub_first_name = request.POST.get('sub_user_first_name_' + str(i))
                sub_last_name = request.POST.get('sub_user_last_name_' + str(i))
                relationship_item = {
                    'relationship_type': {
                        'name': relationship_type
                    },
                    'main_user': {
                        'user_id': int(main_id),
                        'first_name': main_first_name,
                        'last_name': main_last_name
                    },
                    'sub_user': {
                        'user_id': int(sub_id),
                        'first_name': sub_first_name,
                        'last_name': sub_last_name
                    },
                    'created_timestamp': created_date,
                    'last_updated_timestamp': modified_date
                }
                summary_relationships.append(relationship_item)
        if success:
            relationships_list = data.get("relationships", [])
            page = data.get("page", {})
 
            context = {
                    'agent_id':agent_id,
                    'permissions': permissions,
                    'search_count': page.get('total_elements', 0),
                    'relationships': relationships_list,
                    'summary_relationships': summary_relationships,
                    'relationship_type_id':list_relationship_type,
                    'relationship_types': relationship_types,
                    'default_tab': 1,
                    'partner_role': partner_role,
                    'relationship_partner_id':relationship_partner_id or None,
                    'relationship_list_length': relationship_count
                }

            # import pdb;
            # pdb.set_trace()

        self.logger.info('========== finish search relationship ==========')
        
        return render(request, self.template_name, context)

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
