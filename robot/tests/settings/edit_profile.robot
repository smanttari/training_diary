*** Settings ***
Documentation     Tests for editing profile.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App


*** Test Cases ***
Editing profile
    Given settings page is opened
    When user enters "James" to first name
    And user enters "Bond" to last name
    And user enters "james.bond@mail.com" to email
    And user saves changes
    Then message should be "Profiili tallennettu."

Saving Invalid Email Should Fail
    Given settings page is opened
    When user enters "invalid.email" to email
    And user saves changes
    Then no messages should exists


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

User Enters "${first_name}" To First Name
    Input Text      id_first_name   ${first_name}

User Enters "${last_name}" To Last Name
    Input Text      id_last_name    ${last_name}

User Enters "${email}" To Email
    Input Text      id_email        ${email}

User Saves Changes
    Click Button        profile_save