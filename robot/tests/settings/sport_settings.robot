*** Settings ***
Documentation     Tests for editing sport settings.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Get Current Count Of Sports


*** Variables ***
${SPORT_COUNT}     Value set dynamically at test setup.


*** Test Cases ***
Adding A New Sport
    Given settings page is opened
    When user goes to sport sheet
    And user clicks add new
    And user enters sport shorthand: "G"
    And user enters sport name: "Gym"
    And user enters sport group: "Strength"
    And user saves changes
    Then message should be "Muutokset tallennettu."

Adding A New Sport Without Shorthand Should Fail
    Given settings page is opened
    When user goes to sport sheet
    And user clicks add new
    And user saves changes
    Then no messages should exists

Adding A New Sport Without Name Should Fail
    Given settings page is opened
    When user goes to sport sheet
    And user clicks add new
    And user enters sport shorthand: "X"
    And user saves changes
    Then no messages should exists

Editing Sport
    Given settings page is opened
    When user goes to sport sheet
    And user changes sport shorthand in first row to "Gy"
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And sport shorthand in first row should be "Gy"

Deleting Sport
    Given settings page is opened
    When user goes to sport sheet
    And user clicks delete for the first item
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And table contains one row less than before

Deleting Sport That Is In Use Should Fail
    Given settings page is opened
    When user goes to sport sheet
    And user clicks delete for the first item
    And user saves changes
    Then message should be "Lajia ei voida poistaa, koska siihen on liitetty harjoituksia."


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Get Current Count Of Sports
    Connect To Treenit Database
    ${user_id} =    Query  SELECT id FROM auth_user WHERE username = '${USERNAME}'
    ${count} =  Query   SELECT COUNT(id) FROM treenipaivakirja_laji WHERE user_id = ${user_id}[0][0]
    Set Test Variable  ${SPORT_COUNT}  ${count}[0][0]

Settings Page Is Opened
    Click Link    	    nav_user
    Click Link    	    nav_settings

User Goes To Sport Sheet
    Click Link      btn_sports

User Clicks Add New
    Click Button    sports_add

User Enters Sport Shorthand: "${sport_shorthand}"
    Input Text      id_laji_set-${SPORT_COUNT + 1}-laji     ${sport_shorthand}

User Enters Sport Name: "${sport}"
    Input Text      id_laji_set-${SPORT_COUNT + 1}-laji_nimi     ${sport}

User Enters Sport Group: "${sport_group}"
    Input Text      id_laji_set-${SPORT_COUNT + 1}-laji_ryhma     ${sport_group}

User Changes Sport Shorthand In First Row To "${sport_shorthand}"
    Input Text      id_laji_set-0-laji     ${sport_shorthand}

User Clicks Delete For The First Item
    Click Button    id_laji_set-0-del

User Saves Changes
    Click Button    sports_save

Sport Shorthand In First Row Should Be "${sport_shorthand}"
    Textfield Value Should Be     id_laji_set-0-laji     ${sport_shorthand}

Table Contains One Row Less Than Before
    Element Should Not Be Visible   id_laji_set-${SPORT_COUNT - 1}-laji