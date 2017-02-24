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

verify a page should display home page
	Page Should Contain    Welcome