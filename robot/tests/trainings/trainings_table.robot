*** Settings ***
Documentation     Tests for trainings table functionalities.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App


*** Test Cases ***
Filter By Sport
    Given trainings page is opened
    When user selects "Running"
    Then column Laji should contain "Running"
    And total duration should be "2 / 2h"
    And total distance should be "20 / 20km"

Filter By Sport Group
    Given trainings page is opened
    When user selects "Skiing"-group
    Then column Laji should contain "Skiing (classic)"
    And column Laji should contain "Skiing (free)"
    And total duration should be "2.8 / 2.8h"
    And total distance should be "36 / 36km"

Filter By Valid Date Range
    Given trainings page is opened
    When user sets startdate to "25.12.2019"
    And user sets enddate to "25.12.2019"
    Then date should be "2019-12-25 KE"
    And table should contain "1 - 1"-rows

Filter By Invalid Date Range
    Given trainings page is opened
    When user sets startdate to "26.12.2019"
    And user sets enddate to "25.12.2019"
    Then table should contain "0 - 0"-rows

Toggle Rest Days
    Given trainings page is opened
    When user toggles rest days
    Then table should contain "1 - 4"-rows
    When user toggles rest days
    Then column Laji should contain "Lepo"

Change Table Length
    Given trainings page is opened
    When user changes table length to "50"
    Then table should contain "1 - 50"-rows

Go To Next Page
    Given trainings page is opened
    And table length is "25"
    When user goes to next page
    Then table should contain "26 - 50"-rows

Go To Previous Page
    Given trainings page is opened
    And table length is "25"
    And table page "2" is selected
    When user goes to previous page
    Then table should contain "1 - 25"-rows

Search Trainings
    Given trainings page is opened
    When user search for word "Trail run"
    Then comment should be "Trail running"
    And table should contain "1 - 1"-rows

Toggle Details
    Given trainings page is opened
    When user search for word "Intervals"
    And user toggles details
    Then details table is visible
    When user toggles details
    Then details table is not visible

Check Format For Duration-column
    Given trainings page is opened
    When user search for word "Ylläs"
    Then duration should be "01:45"

Disabling Rest Days Checkbox
    Given trainings page is opened
    When user selects "Running"
    Then rest days checkbox should be disabled
    When user selects "Kaikki"-group
    Then rest days checkbox should be enabled


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

Table Length Is "${length}"
    Select From List By Label       treenit_length      ${length}

Table Page "${2}" Is Selected
    Click Link      2

User Selects "${sport}"
    Select From List By Label       sport       ${SPACE*3}${sport}

User Selects "${sport}"-group
    Select From List By Label       sport       ${sport}

User Sets Startdate To "${date}"
    Input Text  startdate   ${date}  

User Sets Enddate To "${date}"
    Input Text  enddate   ${date} 
    Press Keys  enddate     ENTER 

User Toggles Rest Days
    Click Element   restdays  

User Changes Table Length to "${length}"
    Select From List By Label       treenit_length      ${length}

User Goes To Next Page
    Click Element   treenit_next 

User Goes To Previous Page
    Click Element   treenit_previous 

User Search For Word "${word}"
    Input Text  jquery:.dataTables_filter input     ${word}

User Toggles Details
    Click Element   xpath://td[contains(@class, 'details-control')]
    
Column Laji Should Contain "${sport}"
    Table Column Should Contain     treenit     4       ${sport}

Table Should Contain "${row_count}"-rows
    Element Should Contain  treenit_info    ${row_count}

Total Duration Should Be "${duration}"
    Table Cell Should Contain    treenit     -1       5       ${duration}

Total Distance Should Be "${distance}"
    Table Cell Should Contain    treenit     -1       7       ${distance}

Comment Should Be "${comment}"
    Table Cell Should Contain    treenit     2       -3       ${comment}

Date Should Be "${date}"
    Table Cell Should Contain    treenit     2       3       ${date}

Duration Should Be "${duration}"
    Table Cell Should Contain    treenit     2       5       ${duration}

Details Table Is Visible
    Element Should Be Visible       details_table

Details Table Is Not Visible
    Element Should Not Be Visible       details_table

Rest Days Checkbox Should Be Disabled
    Element Should Be Disabled      lepo

Rest Days Checkbox Should Be Enabled
    Element Should Be Enabled      lepo