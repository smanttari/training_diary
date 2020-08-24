*** Settings ***
Documentation     Tests for deleting trainings.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Get Latest Training Id


*** Variables ***
${LATEST_TRAINING_ID}     Value set dynamically at test setup.


*** Test Cases ***
Delete Training
    Given trainings page is opened
    And rest days are toggled off
    When user clicks delete for the latest training
    And user confirms deleting
    Then trainings page should be open
    And message should be "Harjoitus poistettu."

Cancel Deleting
    Given trainings page is opened
    And rest days are toggled off
    When user clicks delete for the latest training
    And user cancels deleting
    Then trainings page should be open
    And no messages should exists


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

User Clicks Delete For The Latest Training
    Click Link      delete_${LATEST_TRAINING_ID}

User Confirms Deleting
    Click Button    yes

User Cancels Deleting
    Click Button    no