*** Settings ***
Documentation     Tests for editing trainings.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Get Latest Training Id


*** Variables ***
${LATEST_TRAINING_ID}     Value set dynamically at test setup.


*** Test Cases ***
Edit Training
    Given trainings page is opened
    And rest days are toggled off
    When user clicks modify for the latest training
    And user enters "1"h "25"min To Duration
    And user saves changes
    Then trainings page should be open
    And message should be "Harjoitus tallennettu."
    And duration should be "01:25" for the latest training

Cancel Editing
    Given trainings page is opened
    And rest days are toggled off
    When user clicks modify for the latest training
    And user enters "20"km to distance
    And user cancels changes
    Then trainings page should be open
    And no messages should exists
    And distance should be "14" for the latest training


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Trainings Page Is Opened
    Click Link      nav_trainings
    Click Link      nav_trainings_list

Rest Days Are Toggled Off
    Click Element   restdays  

User Clicks Modify For The Latest Training
    Click Link      modify_${LATEST_TRAINING_ID}

User Enters "${h}"h "${min}"min To Duration
    Input Text      id_kesto_h      ${h}
    Input Text      id_kesto_min    ${min}

User Enters "${distance}"km To Distance
    Input Text      id_matka        ${distance}

Duration Should Be "${duration}" For The Latest Training
    Click Element   restdays 
    Table Cell Should Contain    treenit     2       5       ${duration}

Distance Should Be "${distance}" For The Latest Training
    Click Element   restdays 
    Table Cell Should Contain    treenit     2       7       ${distance}

User Saves Changes
    Click Button      save 

User Cancels Changes
    Click Link      cancel 