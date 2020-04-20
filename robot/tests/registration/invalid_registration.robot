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
    Click Link      Rekisteröidy

Go To Login Page
    Click Link      KIRJAUDU SISÄÄN

User Enters "${user}" To Username Box
    Input Text      id_username     ${user}

User Enters "${password}" To Password Box
    Input Text      id_password1    ${password} 

User Enters "${password2}" To Password Verification Box
    Input Text      id_password2    ${password2} 
    
User Clicks Rekisteröidy
    Click Button    id_register

Registration Should Fail
    [Arguments]    ${username}    ${password}   ${password2}
    User Enters "${username}" To Username Box
    User Enters "${password}" To Password Box
    User Enters "${password2}" To Password Verification Box
    User Clicks Rekisteröidy
    Registration Page Should Be Open