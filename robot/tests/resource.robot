*** Settings ***
Documentation     A resource file with reusable keywords and variables.
Library           SeleniumLibrary
Library           DatabaseLibrary
Library           DjangoORM.py    ${APP_ROOT}


*** Variables ***
${SERVER}         127.0.0.1:8000
${BROWSER}        Chrome     
${DELAY}          0.1
${URL}            http://${SERVER}/treenipaivakirja/
${APP_ROOT}       ../treenit
${DATABASE}       ${APP_ROOT}/treenit.sqlite3
${USERNAME}       test_user
${PASSWORD}       top_secret12


*** Keywords ***
Create Test User
    Setup Testdata     ${USERNAME}   ${PASSWORD}  

Delete Test User
    Remove Testdata     ${USERNAME}

Open App
    Open Browser    ${URL}accounts/login/   ${BROWSER}
    Maximize Browser Window
    Set Selenium speed  ${DELAY}
    Login Page Should Be Open

Close App
    Close Browser

Login Page Should Be Open
    Location Should Contain     ${URL}accounts/login/
    Title Should Be             Treenipäiväkirja | Login

Registration Page Should Be Open
    Location Should Contain     ${URL}register
    Title Should Be             Treenipäiväkirja | Rekisteröidy

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

Delete Account
    Click Link    	nav_user
    Click Link    	nav_settings
    Click Link		btn_delete_profile
    Click Button	profile_del

Message Should Be "${message}"
    Element Should Be Visible	message_box
	Element Text Should Be		message_text		${message}

No Messages Should Exists
    Element Should Not Be Visible	message_box

Connect To Treenit Database
    Connect To Database Using Custom Params    sqlite3    database="${DATABASE}"

Get Latest Training Id
    Connect To Treenit Database
    ${user_id} =    Query  SELECT id FROM auth_user WHERE username = '${USERNAME}'
    ${id} =  Query   SELECT MAX(id) FROM treenipaivakirja_harjoitus WHERE user_id = ${user_id}[0][0]
    Set Test Variable  ${LATEST_TRAINING_ID}  ${id}[0][0]