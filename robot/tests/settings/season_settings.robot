*** Settings ***
Documentation     Tests for editing training seasons.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Get Current Count Of Seasons


*** Variables ***
${SEASON_COUNT}     Value set dynamically at test setup.


*** Test Cases ***
Adding A New Season
    Given settings page is opened
    When user goes to season sheet
    And user clicks add new
    And user enters season name: "2020-2021"
    And user enters start date: "30.5.2020"
    And user enters end date: "28.2.2021"
    And user saves changes
    Then message should be "Muutokset tallennettu."

Adding A Season Without Name Should Fail
    Given settings page is opened
    When user goes to season sheet
    And user clicks add new
    And user enters start date: "30.5.2020"
    And user enters end date: "28.2.2021"
    And user saves changes
    Then no messages should exists

Adding A Season Without Start Date Should Fail
    Given settings page is opened
    When user goes to season sheet
    And user clicks add new
    And user enters season name: "2020-2021"
    And user enters end date: "28.2.2021"
    And user saves changes
    Then no messages should exists

Adding A Season Without End Date Should Fail
    Given settings page is opened
    When user goes to season sheet
    And user clicks add new
    And user enters season name: "2020-2021"
    And user enters start date: "28.2.2021"
    And user saves changes
    Then no messages should exists

Editing Season
    Given settings page is opened
    When user goes to season sheet
    And user changes season name in first row to: "18-19"
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And season name in first row should be "18-19"

Start Date Cannot Be Larger Than End Date
    Given settings page is opened
    When user goes to season sheet
    And user changes start date in first row to: "1.1.2099"
    And user saves changes
    Then message should be "Loppupäivä ei voi olla pienempi kuin alkupäivä."

Deleting Season
    Given settings page is opened
    When user goes to season sheet
    And user clicks delete for the last item
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And table contains one row less than before


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Get Current Count Of Seasons
    Connect To Treenit Database
    ${user_id} =    Query  SELECT id FROM auth_user WHERE username = '${USERNAME}'
    ${count} =  Query   SELECT COUNT(id) FROM treenipaivakirja_kausi WHERE user_id = ${user_id}[0][0]
    Set Test Variable  ${SEASON_COUNT}  ${count}[0][0]

Settings Page Is Opened
    Click Link    	    nav_user
    Click Link    	    nav_settings

User Goes To Season Sheet
    Click Link      btn_seasons

User Clicks Add New
    Click Button    seasons_add

User Enters Season Name: "${name}"
    Input Text      id_kausi_set-${SEASON_COUNT + 1}-kausi     ${name}

User Enters Start Date: "${startdate}"
    Input Text      id_kausi_set-${SEASON_COUNT + 1}-alkupvm     ${startdate}

User Enters End Date: "${enddate}"
    Input Text      id_kausi_set-${SEASON_COUNT + 1}-loppupvm     ${enddate}

User Changes Season Name In First Row To: "${name}"
    Input Text      id_kausi_set-0-kausi     ${name}

User Changes Start Date In First Row To: "${startdate}"
    Input Text      id_kausi_set-0-alkupvm     ${startdate}

User Saves Changes
    Click Button    seasons_save

User Clicks Delete For The Last Item
    Click Button    id_kausi_set-${SEASON_COUNT - 1}-del

Season Name In First Row Should Be "${name}"
    Textfield Value Should Be     id_kausi_set-0-kausi      ${name}

Table Contains One Row Less Than Before
    Element Should Not Be Visible   id_kausi_set-${SEASON_COUNT - 1}-kausi