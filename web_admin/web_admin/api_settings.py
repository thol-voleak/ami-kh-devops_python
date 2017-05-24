# Authentication
LOGIN_URL = 'api-gateway/system-user/v1/oauth/token'
LOGOUT_URL = 'api-gateway/v1/oauth/token/revoke'

# API Management
APIS_URL="api-gateway/v1/apis/"
SERVICES_LIST_URL="api-gateway/v1/services"

# Centralize configuration
SCOPES_URL = "api-gateway/centralize-configuration/v1/scopes"
CONFIGURATION_URL = "api-gateway/centralize-configuration/v1/scopes/{scope}/configurations"
CONFIGURATION_DETAIL_URL = "api-gateway/centralize-configuration/v1/scopes/{scope}/configurations/{key}/"

# Client
CREATE_CLIENT_URL = 'api-gateway/v1/oauths/clients'
CLIENTS_LIST_URL = 'api-gateway/v1/oauths/clients'
UPDATE_CLIENT_URL = 'api-gateway/v1/oauths/clients/{}'
DELETE_CLIENT_URL = 'api-gateway/v1/oauths/clients/{}'
REGENERATE_CLIENT_SECRET_URL = 'api-gateway/v1/oauths/clients/{}/credentials'
SUSPEND_CLIENT_URL = 'api-gateway/v1/oauths/clients/{}/statuses'
ACTIVATE_CLIENT_URL = 'api-gateway/v1/oauths/clients/{}/statuses'

AGENT_TYPES_LIST_URL = 'api-gateway/agent/v1/types'
GET_ALL_CURRENCY_URL = 'api-gateway/centralize-configuration/v1/scopes/global/configurations/currency'
AGENT_TYPE_CREATE_URL = 'api-gateway/agent/v1/types'
AGENT_TYPE_DETAIL_URL = 'api-gateway/agent/v1/types/{}'
ADD_COUNTRY_CODE_URL = 'api-gateway/centralize-configuration/v1/scopes/global/configurations/country'
GLOBAL_CONFIGURATIONS_URL = 'api-gateway/centralize-configuration/v1/scopes/global/configurations'
GET_ALL_PRELOAD_CURRENCY_URL = 'api-gateway/centralize-configuration/v1/currencies'
ADD_CURRENCY_URL = 'api-gateway/centralize-configuration/v1/scopes/global/configurations/currency'
AGENT_TYPE_UPDATE_URL = 'api-gateway/agent/v1/types/{}'
DELETE_AGENT_TYPE_URL = 'api-gateway/agent/v1/types/{}'
# System User
GET_ALL_SYSTEM_USER = 'api-gateway/system-user/v1/users'
SYSTEM_USER_DETAIL_URL = 'api-gateway/system-user/v1/users/{}'
SYSTEM_USER_CREATE_URL = 'api-gateway/system-user/v1/users'
DELETE_SYSTEM_USER_URL = 'api-gateway/system-user/v1/users/{}'
UPDATE_SYSTEM_USER_URL = 'api-gateway/system-user/v1/users/{}'
SYSTEM_USER_CHANGE_PASSWORD_URL = 'api-gateway/system-user/v1/users/{}'
PAYMENT_URL = 'api-gateway/report/v1/payments/orders'

SERVICE_GROUP_LIST_URL = 'api-gateway/payment/v1/service-groups'
SERVICE_GROUP_UPDATE_URL = 'api-gateway/payment/v1/service-groups/{}'
SERVICE_GROUP_DETAIL_URL = 'api-gateway/payment/v1/service-groups/{}'
ADD_SERVICE_GROUP_URL = 'api-gateway/payment/v1/service-groups'
SERVICE_LIST_URL = 'api-gateway/payment/v1/services/'
SERVICE_CREATE_URL = 'api-gateway/payment/v1/services'
SERVICE_DETAIL_URL = 'api-gateway/payment/v1/services/{}'
SERVICE_UPDATE_URL = 'api-gateway/payment/v1/services/{}'
COMPANY_BALANCE_HISTORY = 'api-gateway/agent/v1/companies/balances/histories/'
GET_AGET_BALANCE = "api-gateway/agent/v1/agents/{}/balances"
CREATE_COMPANY_BALANCE = "api-gateway/agent/v1/companies/sofs/{}"
CLIENT_SCOPES = 'api-gateway/v1/oauths/clients/{client_id}/scopes'
ALL_SCOPES_LIST_URL = 'api-gateway/v1/apis'
COMPANY_BALANCE_ADD = 'api-gateway/agent/v1/companies/balances/'
GET_AGENT_BALANCE_BY_CURRENCY = 'api-gateway/agent/v1/agents/{agent_id}/balances/{currency}'
COMMAND_LIST_BY_SERVICE_URL = 'api-gateway/payment/v1/services/{}/service-commands'
FEE_TIER_LIST = 'api-gateway/payment/v1/service-commands/{service_command_id}/fee-tiers'
COMMAND_LIST_URL = 'api-gateway/payment/v1/commands/'
SERVICE_COMMAND_ADD_URL = 'api-gateway/payment/v1/service-commands/'
ADD_TIER_URL = 'api-gateway/payment/v1/service-commands/{service_command_id}/fee-tiers/'
FEE_TIER_CONDITION_URL = 'api-gateway/payment/v1/fee-tier-conditions/'
AMOUNT_TYPES_URL = 'api-gateway/payment/v1/amount-types'
COMMAND_LIST_URL = 'api-gateway/payment/v1/commands/'
BALANCE_DISTRIBUTION_URL = 'api-gateway/payment/v1/fee-tiers/{fee_tier_id}/balance-distributions'
ACTION_TYPES_URL = 'api-gateway/payment/v1/action-types'
AMOUNT_TYPES_URL = 'api-gateway/payment/v1/amount-types'
SOF_TYPES_URL = 'api-gateway/payment/v1/sof-types'
ACTOR_TYPES_URL = 'api-gateway/payment/v1/actor-types'
TIER_DETAIL_URL = 'api-gateway/payment/v1/fee-tiers/{fee_tier_id}/balance-distributions'
BALANCE_DISTRIBUTION_DETAIL_URL = 'api-gateway/payment/v1/balance-distributions/{balance_distribution_id}'
BONUS_DISTRIBUTION_URL = 'api-gateway/payment/v1/fee-tiers/{fee_tier_id}/bonus-distributions'
BALANCE_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/v1/balance-distributions/{balance_distribution_id}'
BONUS_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/v1/bonus-distributions/{bonus_distributions_id}'
BONUS_SETTINGS_DELETE_PATH = 'api-gateway/payment/v1/bonus-distributions/{bonus_distribution_id}'
TIER_PATH = 'api-gateway/payment/v1/fee-tiers/{}'
GET_BONUS_TYPES_PATH = 'api-gateway/payment/v1/bonus-types'
GET_FEE_TYPES_PATH = 'api-gateway/payment/v1/fee-types'
AGENT_FEE_DISTRIBUTION_URL = 'api-gateway/payment/v1/fee-tiers/{fee_tier_id}/agent-fee-distributions'
AGENT_BONUS_DELETE_PATH = 'api-gateway/payment/v1/agent-bonus-distributions/{agent_bonus_distribution_id}'
# Agent bonus distribution url
AGENT_BONUS_DISTRIBUTION_URL = "api-gateway/payment/v1/fee-tiers/{tf_fee_tier_id}/agent-bonus-distributions"
AGENT_FEE_DISTRIBUTION_DETAIL_URL = 'api-gateway/payment/v1/agent-fee-distributions/{agent_fee_distribution_id}'
AGENT_BONUS_DISTRIBUTION_UPDATE_URL = "api-gateway/payment/v1/agent-bonus-distributions/{agent_bonus_distribution_id}"
FEE_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/v1/bonus-distributions/{fee_distributions_id}'
SERVICE_COMMAND_DELETE_PATH = 'api-gateway/payment/v1/service-commands/{}'
# Agent
AGENT_LIST_PATH = 'api-gateway/agent/v1/agents'
SEARCH_AGENT = 'api-gateway/report/v1/agents'
AGENT_DETAIL_PATH = 'api-gateway/agent/v1/agents/{agent_id}/profiles'
AGENT_REGISTRATION_URL = 'api-gateway/agent/v1/agents/profiles'
CREATE_AGENT_IDENTITY_URL = 'api-gateway/agent/v1/agents/{agent_id}/identities'
CREATE_AGENT_BALANCE_URL = 'api-gateway/agent/v1/agents/{agent_id}/sofs/{sof_type}/{currency}'
GET_CURRENCIES_PATH = 'api-gateway/centralize-configuration/v1/scopes/global/configurations/currency'
GET_AGENT_TYPES_PATH = 'api-gateway/agent/v1/types'
AGENT_UPDATE_PATH = 'api-gateway/agent/v1/agents/{agent_id}/profiles'

MEMBER_CUSTOMER_PATH = 'api-gateway/report/v1/customers'
CARD_LIST_PATH = 'api-gateway/report/v1/cards'
SEARCH_SYSTEM_USER = 'api-gateway/report/v1/system-users'
CARD_HISTORY_PATH = 'api-gateway/report/v1/cards/histories'
GET_CENTRALIZE_CONFIGURATION_URL = "api-gateway/centralize-configuration/prepaid-card/default"
CASH_TRANSACTIONS_URL = "api-gateway/report/v1/cash/transactions"
CASH_SOFS_URL = "api-gateway/report/v1/cash/sofs"
