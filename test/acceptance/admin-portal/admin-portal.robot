*** Settings ***
Test Teardown     Close All Browsers
Resource          ../keywords/common_keyword.robot
Resource          ../keywords/authentication_keyword.robot

*** Test Cases ***
TC_EQTR_00000 Open admin portal
    [Documentation]    To ensure that open admin portal
    #pybot admin-portal.robot
    When user open admin portal
    Then page should display admin portal page
