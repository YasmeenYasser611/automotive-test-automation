*** Settings ***
Resource    ../resources/common.resource

*** Test Cases ***
Valid CAN Frame Passes
    [Tags]    smoke
    Validate CAN Frame    0x123    4    0x11    0x22    0x33    0x00

CAN ID Too Large Is Rejected
    [Tags]    negative
    Run Keyword And Expect Error
    ...    *Invalid CAN ID*
    ...    Validate CAN Frame    0x800    0

DLC Mismatch Is Rejected
    [Tags]    negative
    Run Keyword And Expect Error
    ...    *DLC is 2 but got 1 data bytes*
    ...    Validate CAN Frame    0x100    2    0x11

Overvoltage Flag Is Detected
    Validate CAN Frame    0x200    4    0x00    0x00    0x00    0x02
    Can Overvoltage Flag Should Be    True

Undervoltage Flag Is Detected
    Validate CAN Frame    0x200    4    0x00    0x00    0x00    0x10
    Can Undervoltage Flag Should Be    True

Flags Are Clear
    Validate CAN Frame    0x200    4    0x00    0x00    0x00    0x00
    Can Overvoltage Flag Should Be    False
    Can Undervoltage Flag Should Be    False