*** Settings ***
Documentation     Valid login.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Open App
Suite Teardown    Remove Test Data And Close App


*** Test Cases ***
Valid Login
    Given login page is opened
    When user enters valid username
    And user enters valid password
    And user clicks Login
    Then index page should be open
    

*** Keywords ***
Setup Test Data And Open App
    Create Test User
    Open App   

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Login Page Is Opened
    Click Link      nav_log_in

User Enters Valid Username
    Input Text      id_username     ${USERNAME}

User Enters Valid Password
    Input Text      id_password     ${PASSWORD} 
    
User Clicks Login
    Click Button    id_login