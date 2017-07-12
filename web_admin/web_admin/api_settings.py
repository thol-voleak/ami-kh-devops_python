# Authentication
LOGIN_URL = 'api-gateway/v1/system-user/oauth/token'
LOGOUT_URL = 'api-gateway/v1/oauth/token/revoke'

# API Management
APIS_URL="api-gateway/v1/apis/"
SERVICES_LIST_URL="api-gateway/v1/services"

# Centralize configuration
SCOPES_URL = "api-gateway/centralize-configuration/v1/scopes"
CONFIGURATION_URL = "api-gateway/centralize-configuration/v1/scopes/{scope}/configurations"
CONFIGURATION_DETAIL_URL = "api-gateway/centralize-configuration/v1/scopes/{scope}/configurations/{key}"

# Client
CREATE_CLIENT_URL = 'api-gateway/v1/admin/oauth/clients'
CLIENTS_LIST_URL = 'api-gateway/v1/admin/oauth/clients'
UPDATE_CLIENT_URL = 'api-gateway/v1/admin/oauth/clients/{}'
DELETE_CLIENT_URL = 'api-gateway/v1/admin/oauth/clients/{}'
REGENERATE_CLIENT_SECRET_URL = 'api-gateway/v1/admin/oauth/clients/{}/credentials'
SUSPEND_CLIENT_URL = 'api-gateway/v1/admin/oauth/clients/{}/statuses'
ACTIVATE_CLIENT_URL = 'api-gateway/v1/admin/oauth/clients/{}/statuses'

# Agent Type
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

# Agent
AGENT_LIST_PATH = 'api-gateway/report/v1/agents'
SEARCH_AGENT = 'api-gateway/report/v1/agents'
AGENT_DETAIL_PATH = 'api-gateway/agent/v1/agents/{agent_id}/profiles'
AGENT_REGISTRATION_URL = 'api-gateway/agent/v1/agents'
AGENT_DELETE_URL = 'api-gateway/agent/v1/agents/{agent_id}'
CREATE_AGENT_IDENTITY_URL = 'api-gateway/agent/v1/agents/{agent_id}/identities'
CREATE_AGENT_BALANCE_URL = 'api-gateway/agent/v1/agents/{agent_id}/sofs/{sof_type}/{currency}'
GET_CURRENCIES_PATH = 'api-gateway/centralize-configuration/v1/scopes/global/configurations/currency'
GET_AGENT_TYPES_PATH = 'api-gateway/agent/v1/types'
AGENT_UPDATE_PATH = 'api-gateway/agent/v1/agents/{agent_id}/profiles'

# System User
SEARCH_SYSTEM_USER = 'api-gateway/report/v1/system-users'
CREATE_SYSTEM_USER_URL = 'api-gateway/system-user/v1/admin/system-users'
DELETE_SYSTEM_USER_URL = 'api-gateway/system-user/v1/admin/system-users/{}'
UPDATE_SYSTEM_USER_URL = 'api-gateway/system-user/v1/admin/system-users/{}'
CHANGE_PASSWORD_SYSTEM_USER_URL = 'api-gateway/system-user/v1/admin/system-users/{}/passwords'

# Payment
PAYMENT_URL = 'api-gateway/report/v1/payments/orders'

# Permission
PERMISSION_LIST = 'api-gateway/report/v1/permissions'
CREATE_PERMISSION_PATH = 'api-gateway/system-user/v1/admin/permissions'
PERMISSION_DELETE_PATH = 'api-gateway/system-user/v1/permissions/{permission_id}'

# Roles
ROLE_LIST = 'api-gateway/report/v1/roles'
CREATE_ROLE_PATH = 'api-gateway/system-user/v1/admin/roles'
ROLE_DETAIL_PATH = 'api-gateway/system-user/v1/roles/{role_id}'
ROLE_PERMISSION_PATH = 'api-gateway/system-user/v1/admin/roles/{role_id}/permissions'
USER_ROLE_PATH = 'api-gateway/system-user/v1/roles/{role_id}/users'
ROLE_USER_PATH = 'api-gateway/system-user/v1/users/{user_id}/roles'

# SPI URL
SPI_LIST_PATH = 'api-gateway/payment/v1/service-commands/{}/spi-urls'
SPI_TYPES_PATH = 'api-gateway/payment/v1/spi-url-types'
SPI_ADD_PATH = 'api-gateway/payment/v1/service-commands/{}/spi-urls'
SPI_DETAIL_PATH = 'api-gateway/payment/v1/spi-urls/{spiUrlId}'
SPI_UPDATE_PATH = 'api-gateway/payment/v1/spi-urls/{spiUrlId}'
SPI_DELETE_PATH = 'api-gateway/payment/v1/spi-urls/{spi_url_id}'

# Service Group
SERVICE_GROUP_LIST_URL = 'api-gateway/payment/v1/service-groups'
SERVICE_GROUP_UPDATE_URL = 'api-gateway/payment/v1/service-groups/{}'
SERVICE_GROUP_DETAIL_URL = 'api-gateway/payment/v1/service-groups/{}'
ADD_SERVICE_GROUP_URL = 'api-gateway/payment/v1/service-groups'
DELETE_SERVICE_GROUP_URL = 'api-gateway/payment/v1/service-groups/{}'
GET_SERVICE_URL  = 'api-gateway/payment/v1/service-groups/{serviceGroupId}/services'
GET_ALL_SERVICE_URL  = 'api-gateway/payment/v1/services'

# Service
SERVICE_LIST_URL = 'api-gateway/payment/v1/services/'
SERVICE_CREATE_URL = 'api-gateway/payment/v1/services'
SERVICE_DETAIL_URL = 'api-gateway/payment/v1/services/{}'
SERVICE_UPDATE_URL = 'api-gateway/payment/v1/services/{}'
SERVICE_DELETE_URL = 'api-gateway/payment/v1/services/{}'

# Company Balance
COMPANY_BALANCE_HISTORY = 'api-gateway/agent/v1/companies/balances/histories/'
GET_AGET_BALANCE = "api-gateway/agent/v1/agents/{}/balances"
CREATE_COMPANY_BALANCE = "api-gateway/agent/v1/companies/sofs/{}"
CLIENT_SCOPES = 'api-gateway/v1/admin/oauth/clients/{client_id}/scopes'
ALL_SCOPES_LIST_URL = 'api-gateway/v1/admin/apis'
COMPANY_BALANCE_ADD = 'api-gateway/agent/v1/companies/balances/'
GET_AGENT_BALANCE_BY_CURRENCY = 'api-gateway/agent/v1/agents/{agent_id}/balances/{currency}'

# Command
COMMAND_LIST_BY_SERVICE_URL = 'api-gateway/payment/v1/services/{}/service-commands'
COMMAND_LIST_URL = 'api-gateway/payment/v1/commands/'
SERVICE_COMMAND_ADD_URL = 'api-gateway/payment/v1/service-commands/'

#Tier
FEE_TIER_LIST = 'api-gateway/payment/v1/service-commands/{service_command_id}/fee-tiers'
ADD_TIER_URL = 'api-gateway/payment/v1/service-commands/{service_command_id}/fee-tiers/'
FEE_TIER_CONDITION_URL = 'api-gateway/payment/v1/fee-tier-conditions/'

# Balance Movement
AMOUNT_TYPES_URL = 'api-gateway/payment/v1/amount-types'
BALANCE_DISTRIBUTION_URL = 'api-gateway/payment/v1/fee-tiers/{fee_tier_id}/balance-distributions'
ACTION_TYPES_URL = 'api-gateway/payment/v1/action-types'
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

# Agent Bonus Distribution
AGENT_BONUS_DISTRIBUTION_URL = "api-gateway/payment/v1/fee-tiers/{tf_fee_tier_id}/agent-bonus-distributions"
AGENT_FEE_DISTRIBUTION_DETAIL_URL = 'api-gateway/payment/v1/agent-fee-distributions/{agent_fee_distribution_id}'
AGENT_BONUS_DISTRIBUTION_UPDATE_URL = "api-gateway/payment/v1/agent-bonus-distributions/{agent_bonus_distribution_id}"
FEE_DISTRIBUTION_UPDATE_URL = 'api-gateway/payment/v1/bonus-distributions/{fee_distributions_id}'
SERVICE_COMMAND_DELETE_PATH = 'api-gateway/payment/v1/service-commands/{}'

# Member Customer
MEMBER_CUSTOMER_PATH = 'api-gateway/report/v1/customers'
CARD_LIST_PATH = 'api-gateway/report/v1/cards'
CARD_HISTORY_PATH = 'api-gateway/report/v1/cards/histories'
GET_CENTRALIZE_CONFIGURATION_URL = "api-gateway/centralize-configuration/prepaid-card/default"
CASH_TRANSACTIONS_URL = "api-gateway/report/v1/cash/transactions"
CASH_SOFS_URL = "api-gateway/report/v1/cash/sofs"
BANK_SOFS_URL = "report/v1/banks/sofs"

# Reconcile
SEARCH_RECONCILE_PARTNER_FILE_LIST = 'api-gateway/report/v1/reconciled/partners'
SEARCH_RECONCILE_SOF_FILE_LIST = 'api-gateway/report/v1/reconciled/sofs'
SEARCH_RECONCILE_SOF_REPORT = 'api-gateway/report/v1/reconciled/sofs/results'
SEARCH_RECONCILE_PARTNER_REPORT = 'api-gateway/report/v1/reconciled/partners/results'
GET_SERVICE_BY_SERVICE_GROUP_URL  = 'api-gateway/payment/v1/service-groups/{service_group_id}/services'