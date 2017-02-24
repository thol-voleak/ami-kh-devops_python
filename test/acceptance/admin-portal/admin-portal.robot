*** Settings ***
Test Teardown     Close All Browsers
Resource          ../keywords/common_keyword.robot
Resource          ../keywords/authentication_keyword.robot

*** Test Cases ***
TC_EQTR_00000 Open admin portal
    [Documentation]    To ensure that open admin portal    
    Given user open admin portal
    When page should display admin portal page
    When username is 'admin'
    When password is 'pass99word'
    When user submit login form
    Then verify a page should display home page