*** Settings ***
Resource          ../resources/imports.robot

*** Keywords ***
user open admin portal
    Open Browser    ${admin_web_url}   browser=${browser}
    Maximize Browser Window

user open admin portal client page
    Open Browser    ${admin_web_url}${client_url}   browser=${browser}
    Maximize Browser Window

user go to '${menu_link}' menu
    click element      xpath=//a[@href="/admin-portal/${menu_link}"]

page should display error '${error_message}'
    Wait Until Element Is Visible    id=loginerror
    Element Should Contain    id=loginerror    ${error_message}

page should display login admin portal page
    Page Should Contain    Please login to see this page.

verify a page should display client list page
    Wait Until Page Contains    Client
    element should be visible    //table[@class="table table-bordered table-striped mb0"]
    page should contain      Client Id
    page should contain      Client Name
    page should contain      Created At
    page should contain      Updated At
    page should contain      Created By
