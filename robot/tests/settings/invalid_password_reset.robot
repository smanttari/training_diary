*** Settings ***
Documentation     Invalid password reset.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Go To Password Reset Page
Test Template     Password Reset Should Fail


*** Test Cases ***              OLD_PASSWORD          NEW_PASSWORD          NEW_PASSWORD2                 
Passwords Not Matching          ${PASSWORD}           top_secret12          topsecret12
Short Password                  ${PASSWORD}           invalid               invalid
Password Similar To Username    ${PASSWORD}           ${USERNAME}           ${USERNAME}
Common Password                 ${PASSWORD}           password              password
Numeric Password                ${PASSWORD}           483726189             483726189
Invalid Old Password            invalid               top_secret12          top_secret12
Empty Old Password              ${EMPTY}              top_secret12          top_secret12
Empty New Password              ${PASSWORD}           ${EMPTY}              top_secret12
Empty Password Verification     ${PASSWORD}           top_secret12          ${EMPTY}


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Go To Password Reset Page
    Click Link    	nav_user
    Click Link    	nav_settings
    Click Link      btn_pw_reset

Input Old Password
    [Arguments]    ${old_password} 
    Input Text      id_old_password    ${old_password} 

Input New Password
    [Arguments]    ${new_password} 
    Input Text      id_new_password1    ${new_password} 

Input Password Verification
    [Arguments]    ${new_password2} 
    Input Text      id_new_password2    ${new_password2} 

Saves Changes
    Click Button        pw_save

Password Reset Should Fail
    [Arguments]    ${old_password}    ${new_password}   ${new_password2}
    Input Old Password              ${old_password}
    Input New Password              ${new_password}
    Input Password Verification     ${new_password2} 
    Saves Changes
    No Messages Should Exists