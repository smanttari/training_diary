*** Settings ***
Documentation     Valid registration.
Resource          ../resource.robot
Suite Setup       Open App
Suite Teardown    Close App
Test Teardown     Remove Account


*** Test Cases ***
Valid Registration
    Given registration page is opened
    When user enters "james" to username box
    And user enters "James" to first name box
    And user enters "Bond" to last name box
    And user enters "james.bond@mailbox.com" to email box
    And user enters "top_secret" to password box
    And user enters "top_secret" to password verification box
    And user clicks Rekisteröidy
    Then login page should be open
    And message should be "Käyttäjätili luotu."
    

*** Keywords ***
Registration Page Is Opened
    Click Link      Rekisteröidy

User Enters "${user}" To Username Box
    Input Text      id_username     ${user}

User Enters "${first_name}" To First Name Box
    Input Text      id_first_name   ${first_name}

User Enters "${last_name}" To Last Name Box
    Input Text      id_last_name    ${last_name}

User Enters "${email}" To Email Box
    Input Text      id_email        ${email}

User Enters "${password}" To Password Box
    Input Text      id_password1    ${password} 

User Enters "${password}" To Password Verification Box
    Input Text      id_password2    ${password} 
    
User Clicks Rekisteröidy
    Click Button    id_register

Remove Account
    Log In      james   top_secret
    Delete Account