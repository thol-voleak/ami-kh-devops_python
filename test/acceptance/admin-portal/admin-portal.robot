*** Settings ***
Test Teardown     Close All Browsers
Resource          ../keywords/common_keyword.robot
Resource          ../keywords/authentication_keyword.robot

*** Test Cases ***
TC_EQP_00161 Super user can login on admin portal
    [Documentation]    To ensure that super user can login admin portal
    [Tags]   regression    superuser    login
    Given user open admin portal
    AND username is 'admin'
    AND password is 'pass99word'
    When user submit login form
    Then verify a page should display home page


*** Test Cases ***
TC_EQP_00xxx After super user login success, then can see client list
    [Documentation]    To ensure that super user can login admin portal
    [Tags]   regression    superuser    login
    Given user open admin portal client page
    AND verify a page should display login page
    AND username is 'admin'
    AND password is 'pass99word'
    When user submit login form
    Then verify a page should display client list page
