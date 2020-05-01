*** Settings ***
Documentation     Valid password reset.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App


*** Test Cases ***
Reset Password
    Given settings page is opened
    When user goes to password reset sheet
    When user enters valid old password
    And user enters "NewPW123" to new password
    And user enters "NewPW123" to password verification
    And user saves changes
    Then message should be "Salasana vaihdettu."



*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Settings Page Is Opened
    Click Link    	    nav_user
    Click Link    	    nav_settings

User Goes To Password Reset Sheet
    Click Link      btn_pw_reset

User Enters Valid Old Password
    Input Text      id_old_password    ${PASSWORD} 

User Enters "${password}" To New Password
    Input Text      id_new_password1    ${password} 

User Enters "${password}" To Password Verification
    Input Text      id_new_password2    ${password} 

User Saves Changes
    Click Button        pw_save