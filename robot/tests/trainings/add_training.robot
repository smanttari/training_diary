*** Settings ***
Documentation     Tests for adding new trainings.
Resource          ../resource.robot
Suite Setup       Setup Test Data And Log In
Suite Teardown    Remove Test Data And Close App


*** Test Cases ***
Adding A New Training
    Given trainings form is opened
    When user sets training date to "20.4.2020"
    And user sets time of day to AM
    And user selects "Running" from sport list
    And user enters "1"h "15"min to duration
    And user enters "138" to average heart rate
    And user enters "13.5"km to distance
    And user enters "10,4"km/h to average speed
    And user enters "5:45"min/km to average speed
    And user enters "567" calories
    And user enters "73"m ascent
    And user selects number "7" from feeling list
    And user enters "Nice training" to comment box
    And user saves the training
    Then trainings page should be open
    And message should be "Harjoitus tallennettu."

Adding A Blank Training Should Fail
    Given trainings form is opened
    When user saves the training
    Then trainings form should be open

Adding Training Zones
    Given trainings form is opened
    And sport "Skiing (classic)" is selected
    When user adds zone nro. "1"
    And user select "Aerobic" for zone nro: "1" 
    And user enters "1"h "15"min for zone nro: "1" 
    And user enters "135" avg hr for zone nro: "1"  
    And user enters "20"km for zone nro: "1" 
    And user adds zone nro. "2"
    And user select "Anaerobic" for zone nro: "2" 
    And user enters ""h "30"min for zone nro: "2" 
    And user enters "181" max hr for zone nro: "2" 
    And user enters "3:05"min/km for zone nro: "2" 
    And user saves the training
    Then trainings page should be open
    And message should be "Harjoitus tallennettu."

Adding Training Zone Without Nro Should Fail
    Given trainings form is opened
    And sport "Running" is selected
    When user adds zone
    And user saves the training
    Then trainings form should be open

Adding Training Zone Without Zone Area Should Fail
    Given trainings form is opened
    And sport "Running" is selected
    When user adds zone nro. "1"
    And user saves the training
    Then trainings form should be open


*** Keywords ***
Setup Test Data And Log In
    Create Test User
    Open App
    Log Test User In    

Remove Test Data And Close App
    Log Out
    Delete Test User
    Close Browser

Trainings Form Is Opened
    Click Link      nav_trainings
    Click Link      add_new

Sport "${sport}" Is Selected
    Select From List By Label   id_laji         ${sport}

User Sets Training Date To "${date}"
    Input Text  id_pvm   ${date}  
    Press Keys  id_pvm   ENTER 

User Sets Time Of Day To AM
    Click Element       radio_vuorokaudenaika_0

User Selects "${sport}" From Sport List
    Select From List By Label   id_laji         ${sport}

User Enters "${h}"h "${min}"min To Duration
    Input Text      id_kesto_h      ${h}
    Input Text      id_kesto_min    ${min}

User Enters "${avg_bpm}" To Average Heart Rate
    Input Text      id_keskisyke    ${avg_bpm}

User Enters "${distance}"km To Distance
    Input Text      id_matka        ${distance}

User Enters "${speed_km_h}"km/h To Average Speed
    Input Text      id_vauhti_km_h  ${speed_km_h}

User Enters "${speed_min}:${speed_s}"min/km To Average Speed
    Input Text      id_vauhti_min   ${speed_min} 
    Input Text      id_vauhti_s     ${speed_s}

User Enters "${cal}" Calories
    Input Text      id_kalorit      ${cal}

User Enters "${ascent}"m Ascent
    Input Text      id_nousu        ${ascent}

User Selects Number "${feeling}" From Feeling List
    Select From List By Label       id_tuntuma  ${feeling}

User Enters "${comment}" To Comment Box
    Input Text      id_kommentti    ${comment}

User Saves The Training
    Click Button      save  

Trainings Form Should Be Open
    Location Should Be      ${URL}trainings/add/
    Title Should Be         Treenipäiväkirja | Lisää harjoitus

User Adds Zone
    Click Button    teho_add

User Adds Zone Nro. "${nro}"
    User Adds Zone
    Input Text      id_teho_set-${nro}-nro           ${nro}

User Select "${zone}" For Zone Nro: "${nro}" 
    Select From List By Label       id_teho_set-${nro}-tehoalue      ${zone}

User Enters "${h}"h "${min}"min For Zone Nro: "${nro}" 
    Input Text      id_teho_set-${nro}-kesto_h       ${h}
    Input Text      id_teho_set-${nro}-kesto_min     ${min}

User Enters "${avg_bpm}" Avg HR For Zone Nro: "${nro}"
    Input Text      id_teho_set-${nro}-keskisyke     ${avg_bpm}

User Enters "${max_bpm}" Max HR For Zone Nro: "${nro}"
    Input Text      id_teho_set-${nro}-maksimisyke   ${max_bpm}

User Enters "${distance}"km For Zone Nro: "${nro}"
    Input Text      id_teho_set-${nro}-matka         ${distance}

User Enters "${speed_min}:${speed_s}"min/km For Zone Nro: "${nro}"
    Input Text      id_teho_set-${nro}-vauhti_min    ${speed_min}
    Input Text      id_teho_set-${nro}-vauhti_s      ${speed_s}