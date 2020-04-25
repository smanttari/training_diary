*** Settings ***
Documentation     Invalid registration.
Resource          ../resource.robot
Suite Setup       Open App
Suite Teardown    Close App
Test Setup        Go To Registration Page
Test Teardown     Go To Login Page
Test Template     Registration Should Fail


*** Test Cases ***              USERNAME              PASSWORD           PASSWORD2                 
Passwords Not Matching          testuser1             top_secret         topsecret
Short Password                  testuser2             invalid            invalid
Password Similar To Username    testuser3             testuser34         testuser34
Common Password                 testuser4             password           password
Numeric Password                testuser5             483726189          483726189
Empty Username                  ${EMPTY}              top_secret         top_secret
Empty Password                  testuser6             ${EMPTY}           top_secret
Empty Password Verification     testuser7             top_secret         ${EMPTY}


*** Keywords ***
Go To Registration Page
    Click Link      id_add_account

Go To Login Page
    Click Link      nav_log_in

Input Username
    [Arguments]    ${user}
    Input Text      id_username     ${user}

Input Password
    [Arguments]    ${password}
    Input Text      id_password1    ${password} 

Input Password Verification
    [Arguments]    ${password2}
    Input Text      id_password2    ${password2} 
    
Click Register
    Click Button    id_register

Registration Should Fail
    [Arguments]    ${username}    ${password}   ${password2}
    Input Username  ${username}
    Input Password  ${password}
    Input Password Verification     ${password2}
    Click Register
    Registration Page Should Be Open