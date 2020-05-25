*** Settings ***
Documentation     Invalid login.
Resource          ../resource.robot
Suite Setup       Open App
Suite Teardown    Close App
Test Template     Login Should Fail


*** Test Cases ***        USERNAME             PASSWORD                  
Invalid Password          ${USERNAME}          invalid
Invalid Username          invalid              ${PASSWORD}   
Empty Username            ${EMPTY}             ${PASSWORD}
Empty Password            ${USERNAME}          ${EMPTY}  


*** Keywords ***
Input Username
    [Arguments]    ${user}
    Input Text      id_username     ${user}

Input Pw
    [Arguments]    ${password}
    Input Password      id_password    ${password} 
    
Click Login
    Click Button    id_login

Login Should Fail
    [Arguments]    ${username}    ${password}
    Input Username  ${username}
    Input Pw        ${password}
    Click Login
    Login Page Should Be Open