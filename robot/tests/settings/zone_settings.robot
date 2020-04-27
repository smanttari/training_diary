*** Settings ***
Documentation     Tests for editing zone area settings.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App
Test Setup        Get Current Count Of Zones


*** Variables ***
${ZONE_COUNT}     Value set dynamically at test setup.


*** Test Cases ***
Adding A New Zone
    Given settings page is opened
    When user goes to zone sheet
    And user clicks add New
    And user enters zone nro: "99"
    And user enters zone name: "Maximum"
    And user enters lower boundary: "180"
    And user enters upper boundary: "200"
    And user saves changes
    Then message should be "Muutokset tallennettu."

Adding A Zone Without Nr Should Fail
    Given settings page is opened
    When user goes to zone sheet
    And user clicks add New
    And user saves changes
    Then no messages should exists

Adding A Zone Without Name Should Fail
    Given settings page is opened
    When user goes to zone sheet
    And user clicks add New
    And user enters zone nro: "99"
    And user saves changes
    Then no messages should exists

Editing Zone
    Given settings page is opened
    When user goes to zone sheet
    And user changes upper boundary in first row to: "145"
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And upper boundary in first row should be "145"

Deleting Zone
    Given settings page is opened
    When user goes to zone sheet
    And user clicks delete for the last item
    And user saves changes
    Then message should be "Muutokset tallennettu."
    And table contains one row less than before

Deleting Zone That Is In Use Should Fail
    Given settings page is opened
    When user goes to zone sheet
    And user clicks delete for the first item
    And user saves changes
    Then message should be "Tehoaluetta ei voida poistaa, koska siihen on liitetty harjoituksia."


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Get Current Count Of Zones
    Connect To Treenit Database
    ${user_id} =    Query  SELECT id FROM auth_user WHERE username = '${USERNAME}'
    ${count} =  Query   SELECT COUNT(id) FROM treenipaivakirja_tehoalue WHERE user_id = ${user_id}[0][0]
    Set Test Variable  ${ZONE_COUNT}  ${count}[0][0]

Settings Page Is Opened
    Click Link    	    nav_user
    Click Link    	    nav_settings

User Goes To Zone Sheet
    Click Link      btn_zones

User Clicks Add New
    Click Button    zones_add

User Enters Zone Nro: "${nro}"
    Input Text      id_tehoalue_set-${ZONE_COUNT + 1}-jarj_nro     ${nro}

User Enters Zone Name: "${name}"
    Input Text      id_tehoalue_set-${ZONE_COUNT + 1}-tehoalue     ${name}

User Enters Lower Boundary: "${lower}"
    Input Text      id_tehoalue_set-${ZONE_COUNT + 1}-alaraja     ${lower}

User Enters Upper Boundary: "${upper}"
    Input Text      id_tehoalue_set-${ZONE_COUNT + 1}-ylaraja     ${upper}

User Changes Upper Boundary In First Row To: "${upper}"
    Input Text      id_tehoalue_set-0-ylaraja     ${upper}

User Saves Changes
    Click Button    zones_save

User Clicks Delete For The First Item
    Click Button    id_tehoalue_set-0-del

User Clicks Delete For The Last Item
    Click Button    id_tehoalue_set-${ZONE_COUNT - 1}-del

Upper Boundary In First Row Should Be "${upper}"
    Textfield Value Should Be     id_tehoalue_set-0-ylaraja     ${upper}

Table Contains One Row Less Than Before
    Element Should Not Be Visible   id_tehoalue_set-${ZONE_COUNT - 1}-laji