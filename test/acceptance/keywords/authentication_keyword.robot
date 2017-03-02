*** Settings ***
Resource          ../resources/imports.robot

*** Keywords ***
username is '${username}'
    Wait Until Element Is Visible    id=id_username
    Input Text    id=id_username    ${username}

password is '${password}'
    Input Text    id=id_password    ${password}

user submit login form
    Click Element    id=submitlogin

super user login success
    username is 'admin'
    password is 'pass99word'
    user submit login form
    verify a page should display home page

verify a page should display home page
    Wait Until Page Contains    Home
    Page Should Contain    Welcome

