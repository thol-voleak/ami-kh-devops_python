*** Settings ***
Resource          ../resources/imports.robot

*** Keywords ***
username is '${username}'
    Wait Until Element Is Visible    id=username
    Input Text    id=username    ${username}

password is '${password}'
    Input Text    id=password    ${password}

user submit login form
    Click Element    id=submitlogin
