*** Settings ***
Test Teardown     Close All Browsers
Resource          ../keywords/common_keyword.robot
Resource          ../keywords/authentication_keyword.robot

*** Test Cases ***
TC_EQP_00161 Super user can login on admin portal
    [Documentation]    To ensure that super user can login admin portal
    [Tags]   regression    superuser    login     high
    Given user open admin portal
    AND username is 'admin'
    AND password is 'pass99word'
    When user submit login form
    Then verify a page should display home page


TC_EQP_00162 After super user login success, then can see client list
    [Documentation]    To ensure that super user can see client list all after login success
    [Tags]    regression    superuser    high     client-list
    Given user open admin portal
    AND super user login success
    When user go to 'client-credentials' menu
    Then verify a page should display client list page

TC_EQP_00163 Can't see client id without login
    [Documentation]    To ensure that can't list client id without login and go to login page
    [Tags]    regression    superuser    medium     client-list
    When user open admin portal client page
    Then page should display login admin portal page