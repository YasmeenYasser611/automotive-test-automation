*** Settings ***
Resource    ../resources/common.resource

*** Test Cases ***
ECU Communication Works
    [Tags]    smoke
    Configure ECU Failures    0
    ${status}=    Get Device Status
    Should Be Equal    ${status}    OK

ECU Communication Error Is Meaningful
    [Tags]    negative
    Configure ECU Failures    1
    Run Keyword And Expect Error
    ...    *Failed to communicate with ECU*
    ...    Get Device Status

ECU Communication Is Retried
    [Tags]    smoke
    Configure ECU Failures    2
    ${status}=    Get Device Status With Retry    3    0.1
    Should Be Equal    ${status}    OK

All Retries Fail
    [Tags]    negative
    Configure ECU Failures    3
    Run Keyword And Expect Error
    ...    *Failed to communicate with ECU*
    ...    Get Device Status With Retry    3    0.1

Invalid Retry Count Is Rejected
    [Tags]    negative
    Run Keyword And Expect Error
    ...    *attempts must be greater than zero*
    ...    Get Device Status With Retry    0    0.1