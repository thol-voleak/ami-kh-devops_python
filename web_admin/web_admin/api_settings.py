API_VERSION = 'v3.1'
API_GATEWAY_PATH = 'api-gateway'

# Authentication
LOGIN_URL = 'api-gateway/'+API_VERSION+'/system-user/oauth/token'
LOGOUT_URL = 'api-gateway/'+API_VERSION+'/oauth/token/revoke'
GET_PERMISSION_PATH = 'api-gateway/system-user/'+API_VERSION+'/roles-permissions'

# API Management
APIS_URL = 'api-gateway/'+API_VERSION+'/apis/'
SERVICES_LIST_URL = 'api-gateway/'+API_VERSION+'/admin/services'

# Centralize configuration
SCOPES_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes'
GET_ALL_PRELOAD_CURRENCY_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/currencies'

CONFIGURATION_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/{scope}/configurations'
CONFIGURATION_DETAIL_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/{scope}/configurations/{key}'
CONFIGURATION_UPDATE_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/{scope}/configurations/{key}'
GET_ALL_CURRENCY_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/global/configurations/currency'
ADD_COUNTRY_CODE_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/global/configurations/country'
GLOBAL_CONFIGURATIONS_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/global/configurations'
ADD_CURRENCY_URL = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/global/configurations/currency'
GET_CURRENCIES_PATH = 'api-gateway/centralize-configuration/'+API_VERSION+'/admin/scopes/names/global/configurations/currency'

# Client
CREATE_CLIENT_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients'
CLIENTS_LIST_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients'
UPDATE_CLIENT_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{}'
DELETE_CLIENT_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{}'
REGENERATE_CLIENT_SECRET_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{}/credentials'
SUSPEND_CLIENT_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{}/statuses'
ACTIVATE_CLIENT_URL = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{}/statuses'

# Agent Type
# GET_AGENT_IDENTITY_URL = 'api-gateway/report/'+API_VERSION+'/agents/identities'
AGENT_TYPES_LIST_URL = 'api-gateway/report/'+API_VERSION+'/agent-types'

AGENT_TYPE_CREATE_URL = 'api-gateway/agent/'+API_VERSION+'/admin/agent-types'
AGENT_TYPE_DETAIL_URL = 'api-gateway/report/'+API_VERSION+'/agent-types'

AGENT_TYPE_UPDATE_URL = 'api-gateway/agent/'+API_VERSION+'/admin/agent-types/{}'
DELETE_AGENT_TYPE_URL = 'api-gateway/agent/'+API_VERSION+'/admin/agent-types/{}'

# Agent
AGENT_LIST_PATH = 'api-gateway/report/'+API_VERSION+'/agents'
SEARCH_AGENT = 'api-gateway/report/'+API_VERSION+'/agents'
AGENT_DETAIL_PATH = 'api-gateway/report/'+API_VERSION+'/agents'
AGENT_REGISTRATION_URL = 'api-gateway/agent/'+API_VERSION+'/admin/agents'
AGENT_DELETE_URL = 'api-gateway/agent/'+API_VERSION+'/admin/agents/{agent_id}'
CREATE_AGENT_BALANCE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/sofs/cash'
AGENT_UPDATE_PATH = 'api-gateway/agent/'+API_VERSION+'/admin/agents/{agent_id}'
AGENT_ADD_IDENTITY_PATH = 'api-gateway/agent/'+API_VERSION+'/admin/agents/{agent_id}/identities'
AGENT_SMARTCARD_PATH = 'api-gateway/report/'+API_VERSION+'/agents/smartcards'
ADD_AGENT_SMART_CARD_PATH = 'api-gateway/agent/'+API_VERSION+'/admin/agents/{}/smartcards'
DELETE_AGENT_SMART_CARD_PATH = 'api-gateway/agent/'+API_VERSION+'/admin/agents/{}/smartcards/{}'
AGENT_STATUS_URL = 'api-gateway/agent/'+ API_VERSION + '/admin/agents/{}/status'
SEARCH_RELATIONSHIP = 'api-gateway/report/'+API_VERSION+'/agents/relationships'
RELATIONSHIP_TYPES_LIST = 'api-gateway/agent/'+ API_VERSION + '/admin/relationship-types'

GET_AGENT_IDENTITY_URL = 'api-gateway/report/'+API_VERSION+'/agents/identities'
AGENT_IDENTITY_RESET_PASSWORD = 'api-gateway/agent/' + API_VERSION + '/admin/agents/{}/identities/{}/passwords/temporary'
# System User
GET_PROFILE_SYSTEM_USER_PATH = 'api-gateway/system-user/'+API_VERSION+'/system-users/'
SEARCH_SYSTEM_USER = 'api-gateway/report/'+API_VERSION+'/system-users'
CREATE_SYSTEM_USER_URL = 'api-gateway/system-user/'+API_VERSION+'/admin/system-users'
DELETE_SYSTEM_USER_URL = 'api-gateway/system-user/'+API_VERSION+'/admin/system-users/{}'
UPDATE_SYSTEM_USER_URL = 'api-gateway/system-user/'+API_VERSION+'/admin/system-users/{}'
CHANGE_PASSWORD_SYSTEM_USER_URL = 'api-gateway/system-user/'+API_VERSION+'/admin/system-users/{}/passwords'
CHANGE_PASSWD = 'api-gateway/system-user/'+API_VERSION+'/system-users/passwords'

# Payment
PAYMENT_URL = 'api-gateway/report/'+API_VERSION+'/payments/orders'

# Permission
PERMISSION_LIST = 'api-gateway/report/'+API_VERSION+'/permissions'
CREATE_PERMISSION_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/permissions'
PERMISSION_DETAIL_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/permissions/{permission_id}'

# Roles
ROLE_LIST = 'api-gateway/report/'+API_VERSION+'/roles'
CREATE_ROLE_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/roles'
ROLE_DELETE_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/roles/{role_id}'
ROLE_UPDATE_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/roles/{role_id}'
ROLE_PERMISSION_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/roles/{role_id}/permissions'
USER_ROLE_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/roles/{role_id}/system-users'
ROLE_USER_PATH = 'api-gateway/system-user/'+API_VERSION+'/admin/system-users/{user_id}/roles'

# SPI URL
SPI_LIST_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/{}/spi-urls'
SPI_TYPES_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/spi-url-types'
SPI_ADD_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/{}/spi-urls'
SPI_DETAIL_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/spi-urls/{spiUrlId}'
SPI_UPDATE_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/spi-urls/{spiUrlId}'
SPI_DELETE_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/spi-urls/{spi_url_id}'
SPI_CALL_METHOD_PATH = 'api-gateway/payment/'+API_VERSION+'/spi-url-call-methods'

# Service Group
SERVICE_GROUP_LIST_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups'
SERVICE_GROUP_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups/{}'
SERVICE_GROUP_DETAIL_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups/{}'
ADD_SERVICE_GROUP_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups'
DELETE_SERVICE_GROUP_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups/{}'
GET_SERVICE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups/{serviceGroupId}/services'
GET_ALL_SERVICE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services'

# Service
SERVICE_LIST_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services/'
SERVICE_CREATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services'
SERVICE_DETAIL_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services/{}'
SERVICE_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services/{}'
SERVICE_DELETE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services/{}'

# Company Balance
COMPANY_BALANCE_HISTORY = 'api-gateway/payment/'+API_VERSION+'/admin/companies/sofs/cash/balances/histories/'
GET_AGENT_BALANCE = 'api-gateway/report/'+API_VERSION+'/cash/sofs'
CREATE_COMPANY_BALANCE = 'api-gateway/payment/'+API_VERSION+'/admin/companies/sofs/cash'
CLIENT_SCOPES = 'api-gateway/'+API_VERSION+'/admin/oauth/clients/{client_id}/scopes'
ALL_SCOPES_LIST_URL = 'api-gateway/'+API_VERSION+'/admin/apis'
COMPANY_BALANCE_ADD = 'api-gateway/payment/'+API_VERSION+'/admin/companies/sofs/cash/balances/'
GET_AGENT_BALANCE_BY_CURRENCY = 'api-gateway/agent/'+API_VERSION+'/agents/{agent_id}/balances/{currency}'

GET_REPORT_AGENT_BALANCE = 'api-gateway/report/'+API_VERSION+'/cash/sofs'

# Command
COMMAND_LIST_BY_SERVICE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/services/{}/service-commands'
COMMAND_LIST_URL = 'api-gateway/payment/'+API_VERSION+'/commands/'
SERVICE_COMMAND_ADD_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/'

# Tier
FEE_TIER_LIST = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/{service_command_id}/fee-tiers'
ADD_TIER_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/{service_command_id}/fee-tiers/'
FEE_TIER_CONDITION_URL = 'api-gateway/payment/'+API_VERSION+'/fee-tier-conditions/'

# Balance Movement
AMOUNT_TYPES_URL = 'api-gateway/payment/'+API_VERSION+'/admin/amount-types'
BALANCE_DISTRIBUTION_URL = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{fee_tier_id}/balance-distributions'
ACTION_TYPES_URL = 'api-gateway/payment/'+API_VERSION+'/admin/action-types'
SOF_TYPES_URL = 'api-gateway/payment/'+API_VERSION+'/admin/sof-types'
ACTOR_TYPES_URL = 'api-gateway/payment/'+API_VERSION+'/admin/actor-types'
TIER_DETAIL_URL = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{fee_tier_id}/balance-distributions'
BALANCE_DISTRIBUTION_DETAIL_URL = 'api-gateway/payment/'+API_VERSION+'/admin/balance-distributions/{balance_distribution_id}'
BONUS_DISTRIBUTION_URL = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{fee_tier_id}/bonus-distributions'
BALANCE_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/balance-distributions/{balance_distribution_id}'
BONUS_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/bonus-distributions/{bonus_distributions_id}'
BONUS_SETTINGS_DELETE_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/bonus-distributions/{bonus_distribution_id}'
TIER_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{}'
GET_BONUS_TYPES_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/bonus-types'
GET_FEE_TYPES_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/fee-types'
AGENT_FEE_DISTRIBUTION_URL = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{fee_tier_id}/agent-fee-distributions'
AGENT_BONUS_DELETE_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/agent-bonus-distributions/{agent_bonus_distribution_id}'

#Balance Adjustment
ORDER_BAL_ADJUST_PATH = 'api-gateway/workflow/'+API_VERSION+'/admin/adjustments'
APPROVE_BAL_ADJUST_PATH = 'api-gateway/workflow/'+API_VERSION+'/admin/adjustments/{reference_id}'
BALANCE_ADJUSTMENT_PATH = 'api-gateway/report/'+API_VERSION+'/workflows/adjustments'

# Agent Bonus Distribution
AGENT_BONUS_DISTRIBUTION_URL = 'api-gateway/payment/'+API_VERSION+'/admin/fee-tiers/{tf_fee_tier_id}/agent-bonus-distributions'
AGENT_FEE_DISTRIBUTION_DETAIL_URL = 'api-gateway/payment/'+API_VERSION+'/admin/agent-fee-distributions/{agent_fee_distribution_id}'
AGENT_BONUS_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/agent-bonus-distributions/{agent_bonus_distribution_id}'
FEE_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/'+API_VERSION+'/admin/bonus-distributions/{fee_distributions_id}'
SERVICE_COMMAND_DELETE_PATH = 'api-gateway/payment/'+API_VERSION+'/admin/service-commands/{}'

# Member Customer
MEMBER_CUSTOMER_PATH = 'api-gateway/report/'+API_VERSION+'/customers'
BLOCKED_DEVICES_LIST = 'api-gateway/report/'+API_VERSION+'/blocked-devices'
CARD_LIST_PATH = 'api-gateway/report/'+API_VERSION+'/cards'
BALANCE_MOVEMENT_LIST_PATH = 'api-gateway/report/'+API_VERSION+'/payments/orders/balance-movements'
CARD_HISTORY_PATH = 'api-gateway/report/'+API_VERSION+'/cards/histories'
ACTIVATE_CARD_PATH = 'api-gateway/prepaid-card/' + API_VERSION + '/admin/cards/{card_id}/status'

CASH_TRANSACTIONS_URL = 'api-gateway/report/'+API_VERSION+'/cash/transactions'
CASH_SOFS_URL = 'api-gateway/report/'+API_VERSION+'/cash/sofs'
BANK_SOFS_URL = 'report/'+API_VERSION+'/banks/sofs'
LIST_BANK_SOFS_URL = 'api-gateway/report/'+API_VERSION+'/banks/sofs'
CUSTOMER_IDENTITIES_LIST = 'api-gateway/report/'+API_VERSION+'/customers/identities'
SUSPEND_CUSTOMER = 'api-gateway/customer/'+API_VERSION+'/admin/customers/{}/status'
ACTIVATE_CUSTOMER = 'api-gateway/customer/'+API_VERSION+'/admin/customers/{}/status'
RESET_IDENTITY_PASSWORD = 'api-gateway/customer/'+API_VERSION+'/admin/customers/{}/identities/{}/passwords/temporary'
ADMIN_UPDATE_CUSTOMER = 'api-gateway/customer/'+API_VERSION+'/admin/customers/{}'
ADMIN_DELETE_CUSTOMER_URL = 'api-gateway/customer/'+API_VERSION+'/admin/customers/{}'

# Reconcile
SEARCH_RECONCILE_PARTNER_FILE_LIST = 'api-gateway/report/'+API_VERSION+'/reconciled/partners'
SEARCH_RECONCILE_SOF_FILE_LIST = 'api-gateway/report/'+API_VERSION+'/reconciled/sofs'
SEARCH_RECONCILE_SOF_REPORT = 'api-gateway/report/'+API_VERSION+'/reconciled/sofs/results'
SEARCH_RECONCILE_PARTNER_REPORT = 'api-gateway/report/'+API_VERSION+'/reconciled/partners/results'
GET_SERVICE_BY_SERVICE_GROUP_URL = 'api-gateway/payment/'+API_VERSION+'/admin/service-groups/{service_group_id}/services'

# Card Type
SEARCH_CARD_TYPE = 'api-gateway/report/'+API_VERSION+'/card-types'
UPDATE_CARD_TYPE = 'api-gateway/prepaid-card/'+API_VERSION+'/admin/card-types/{card_type_id}'

# Card Design
UPDATE_CARED_PROVIDER = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers/{provider_id}'
GET_DETAIL_PROVIDER = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers/{provider_id}'
SEARCH_CARD_DESIGN = 'api-gateway/report/'+API_VERSION+'/cards/sofs/card-designs'
SEARCH_CARD_PROVIDER ='api-gateway/report/'+API_VERSION+'/cards/sofs/providers'
CREATE_CARD_PROVIDER = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers'
CREATE_CARD_DESIGN = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers/{provider_id}/card-designs'
CARD_DESIGN_DETAIL = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers/{provider_id}/card-designs/{card_id}'
CARD_TYPE_LIST = 'api-gateway/sof-card/'+API_VERSION+'/admin/card-types'
CARD_DESIGN_UPDATE = 'api-gateway/sof-card/'+API_VERSION+'/admin/providers/{provider_id}/card-designs/{card_id}'

# Bank Profile
CREATE_BANK_PROFILE_PATH = "api-gateway/sof-bank/" + API_VERSION + "/admin/banks"
GET_BANK_PROFILE_REPORT_PATH = "api-gateway/report/" + API_VERSION + "/banks"

#fraud consultant
SEARCH_TICKET = 'api-gateway/report/' + API_VERSION + '/tickets'
DELETE_FREEZE_CARD_PATH = 'api-gateway/fraud-consultant/' + API_VERSION +'/admin/tickets/{ticket_id}'
CREATE_FRAUD_TICKET = 'api-gateway/fraud-consultant/'+API_VERSION+'/admin/tickets'
DELETE_FRAUD_TICKET = 'api-gateway/fraud-consultant/'+API_VERSION+'/admin/tickets/{ticket_id}'

#Payment
GET_PAYMENT_DETAIL = 'api-gateway/payment/'+API_VERSION+'/orders/{order_id}'

#Market Campaign
GET_CAMPAIGNS = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules'
UPDATE_CAMPAIGNS = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}'
GET_CAMPAIGNS_DETAIL= 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}'
CREATE_CAMPAIGN = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules'
SEARCH_CAMPAIGNS = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/report'
GET_MECHANIC_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics'
CREATE_MECHANIC = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics'
GET_CONDITION_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics/{bak_mechanic_id}/conditions'
GET_REWARD_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics/{bak_mechanic_id}/actions'
GET_CONDITION_DETAIL = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics/{bak_mechanic_id}/conditions/{bak_condition_id}'
GET_CONDITION_FILTER = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions/{condition_id}/filters'
GET_COMPARISON_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics/{bak_mechanic_id}/conditions/{bak_condition_id}/comparisons'
DELETE_MECHANIC_URL = 'api-gateway/rule-engine/' + API_VERSION + '/admin/rules/{campaign_id}/mechanics/{mechanic_id}'
CREATE_CONDITION = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions'
CREATE_COMPARISON = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions/{condition_id}/comparisons'
CREATE_REWARD =     'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/actions'
CREATE_LIMITATION = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/actions/{action_id}/limits'
GET_LIMITION_LIST= 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{bak_rule_id}/mechanics/{bak_mechanic_id}/actions/{bak_action_id}/limits'
CREATE_FILTER = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions/{condition_id}/filters'

# Rule Engine
GET_RULE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules'
SEARCH_RULE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/report'
CREATE_RULE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules'
GET_RULE_CONDITION_DATA_TYPE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/data-types'
GET_RULE_OPERATION_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/operators'
GET_RULE_DETAIL= 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}'
GET_RULE_MECHANIC_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics'
GET_RULE_CONDITION_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions'
GET_RULE_COMPARISON_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions/{condition_id}/comparisons'
GET_RULE_CONDITION_DETAIL = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/conditions/{condition_id}'
GET_RULE_REWARD_LIST = 'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/actions'
GET_ACTION_TYPE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/action-types'
GET_DATA_TYPE = 'api-gateway/rule-engine/'+API_VERSION+'/admin/data-types'
CREATE_ACTION =     'api-gateway/rule-engine/'+API_VERSION+'/admin/rules/{rule_id}/mechanics/{mechanic_id}/actions'


#Remmittance
GET_VOUCHER_DETAIL = 'api-gateway/report/'+API_VERSION+'/vouchers'
SEARCH_VOUCHERS = 'api-gateway/report/'+API_VERSION+'/vouchers'
UPDATE_HOLD_STATUS = 'api-gateway/voucher/'+API_VERSION+'/admin/vouchers/{voucher_id}/status'

#Report Configuration
GET_WHITELIST_REPORT = 'api-gateway/report/' + API_VERSION + '/admin/payments/summaries/transactions/agents/services'
ADD_SERVICE = 'api-gateway/report/'+API_VERSION+'/admin/payments/summaries/transactions/agents/services'
DELETE_SERVICE = 'api-gateway/report/'+API_VERSION+'/admin/payments/summaries/transactions/agents/services'

# Balance
GET_CUSTOMER_BALANCE=     'api-gateway/report/' + API_VERSION + '/customers/summaries/sofs/cash'
GET_AGENT_SUMMARY= 'api-gateway/report/' + API_VERSION + '/agents/summaries/sofs/cash'

# Category
ADD_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/product-categories'
GET_CATEGORIES = 'api-gateway/report/' + API_VERSION + '/categories'
EDIT_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/product-categories/{category_id}'
DELETE_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/product-categories/{category_id}'

# Product
GET_PRODUCTS = 'api-gateway/report/' + API_VERSION + '/products'
ADD_PRODUCT = 'api-gateway/agent/' + API_VERSION + '/admin/products'
ADD_PRODUCT_AGENT_RELATION = 'api-gateway/agent/' + API_VERSION + '/admin/products/agent-types/relations'
UPDATE_PRODUCT_STATUS_IN_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/products/{product_id}'
GET_PRODUCT_DETAIL = 'api-gateway/report/' + API_VERSION + '/products'
PRODUCT_AGENT_TYPE = 'api-gateway/report/' + API_VERSION + '/products/agent-types/relations'
EDIT_PRODUCT = 'api-gateway/agent/' + API_VERSION + '/admin/products/{product_id}'
DELETE_PRODUCT_AGENT_TYPE_RELATION = 'api-gateway/agent/' + API_VERSION + '/admin/products/agent-types/relations/{product_agent_type_relation_id}'
DELETE_PRODUCT = 'api-gateway/agent/' + API_VERSION + '/admin/products/{product_id}'

# Shop-type
SHOP_TYPE_CREATE = 'api-gateway/agent/' + API_VERSION + '/admin/shop-types'
SHOP_TYPE_DELETE = 'api-gateway/agent/' + API_VERSION + '/admin/shop-types/{shop_type_id}'
GET_SHOP_TYPE_DETAIL = 'api-gateway/report/' + API_VERSION + '/shop-types'
GET_LIST_SHOP_TYPE = 'api-gateway/report/' + API_VERSION + '/shop-types'
EDIT_SHOP_TYPE = 'api-gateway/agent/' + API_VERSION + '/admin/shop-types/{shop_type_id}'

GET_LIST_SHOP_CATEGORIES = 'api-gateway/report/' + API_VERSION + '/shop-categories'
GET_DETAIL_SHOP_CATEGORIES = 'api-gateway/report/' + API_VERSION + '/shop-categories'
CREATE_SHOP_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/shop-categories/'
EDIT_SHOP_CATEGORIES = 'api-gateway/agent/' + API_VERSION + '/admin/shop-categories/{shop_category_id}'
DELETE_SHOP_CATEGORY = 'api-gateway/agent/' + API_VERSION + '/admin/shop-categories/{shop_category_id}'
GET_PRODUCT_AGENT_RELATION = 'api-gateway/report/' + API_VERSION + '/products/agents/relations'
CREATE_PRODUCT_AGENT_RELATION = 'api-gateway/agent/' + API_VERSION + '/admin/products/agents/relations'
DELETE_PRODUCT_AGENT_RELATION = 'api-gateway/agent/' + API_VERSION + '/admin/products/agents/relations/{relation_id}'

GET_DETAIL_SHOP = 'api-gateway/report/' + API_VERSION + '/shops'
