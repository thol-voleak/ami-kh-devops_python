*** Settings ***
Resource          ../resources/imports.robot

*** Keywords ***
user open admin portal
    Open Browser    ${admin_web_url}    browser=${browser}
    Maximize Browser Window

page should display error '${error_message}'
    Wait Until Element Is Visible    id=loginerror
    Element Should Contain    id=loginerror    ${error_message}

page should display welcome page with ‘${username}’
    Page Should Contain    Welcome, ${username}

page should display admin portal page
    Page Should Contain    Please login to see this page.