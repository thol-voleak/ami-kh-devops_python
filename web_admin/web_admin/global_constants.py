from enum import Enum


class UserType(Enum):
    CUSTOMER = 1
    AGENT = 2
    SYSTEM_ADMIN = 3

class SOFType(Enum):
    BANK = 1
    CASH = 2
    CARD = 3

ORDER_STATUS = {
    0:'Created',
    2:'Executed',
    -1:'Fail',
    1:'Locking',
    3:'Rolled back',
    4:'Time out',
    5:'Deleted'
}

ORDER_DETAIL_STATUS = {
    0:'Created',
    2:'Executed',
    -1:'Fail',
    1:'Locking',
    4:'Rolled back',
    3:'Time out'
}

SOF_TYPE = {
    1:'Bank',
    2:'Cash',
    3:'Card'
}

REFUND_STATUS = {
    '1':'CREATING',
    '2':'CREATE_FAIL',
    '3':'CREATED',
    '4':'APPROVING',
    '5':'APPROVE_FAIL',
    '6':'APPROVED',
    '7':'REJECTING',
    '8':'REJECT_FAIL',
    '9':'REJECTED',
    '10':'TIMEOUT'
}