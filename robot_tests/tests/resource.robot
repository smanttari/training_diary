*** Settings ***
Documentation     A resource file with reusable keywords and variables.
Library           SeleniumLibrary
Library           DatabaseLibrary
Library           ../libraries/DjangoORM.py    ${PROJECT_ROOT}


*** Variables ***
${SERVER}         127.0.0.1:8000
${BROWSER}        Chrome     
${DELAY}          0.1
${URL}            http://${SERVER}/treenipaivakirja/
${PROJECT_ROOT}   ../Treenit
${DATABASE}       ${PROJECT_ROOT}/treenit.sqlite3
${USERNAME}       test_user
${PASSWORD}       top_secret

*** Keywords ***
Create Test User
    Setup Testdata     ${USERNAME}   ${PASSWORD}  

Delete Test User
    Remove Testdata     ${USERNAME}

Open Browser To Login Page
    Open Browser    ${URL}accounts/login/   ${BROWSER}
    Maximize Browser Window
    Set Selenium speed  ${DELAY}
    Login Page Should Be Open

Login Page Should Be Open
    Location Should Contain     ${URL}accounts/login/
    Title Should Be             Treenipäiväkirja | Login

Logout Page Should Be Open
    Location Should Contain     ${URL}accounts/logout/
    Title Should Be             Treenipäiväkirja | Logout

Index Page Should Be Open
    Location Should Be      ${URL}
    Title Should Be         Treenipäiväkirja

Trainings Page Should Be Open
    Location Should Be      ${URL}trainings/
    Title Should Be         Treenipäiväkirja | Harjoitukset

Settings Page Should Be Open
    Location Should Be      ${URL}settings/
    Title Should Be         Treenipäiväkirja | Asetukset

Log In 
    [Arguments]    ${user}      ${pass}
    Input Text          id_username    ${user}
    Input Text          id_password    ${pass}
    Click Button        id_login
    Index Page Should Be Open

Log Test User In
    Log In  ${USERNAME}   ${PASSWORD}

Log Out
    Click Link      	nav_user
    Click Link    	    nav_logout
    Logout Page Should Be Open