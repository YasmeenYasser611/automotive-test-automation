*** Settings ***
Documentation    Voltage in, CAN frame 0x123 out: flags in Byte 4 must match the voltage.
Resource         ../resources/common.resource
Test Template    Flags Should Match Voltage

*** Test Cases ***                      VOLTS    OVERVOLTAGE    UNDERVOLTAGE
TC01 Lower valid limit                  5.0      False          True
TC02 Just inside                        5.1      False          True
TC03 Mid undervoltage                   7.0      False          True
TC04 Just below 9 V                     8.9      False          True
TC05 Boundary 9 V                       9.0      False          False
TC06 Just above 9 V                     9.1      False          False
TC07 Mid normal                         11.5     False          False
TC08 Just below 14 V                    13.9     False          False
TC09 Boundary 14 V                      14.0     False          False
TC10 Just above 14 V                    14.1     True           False
TC11 Mid overvoltage                    16.0     True           False
TC12 Just below 18 V                    17.9     True           False
TC13 Upper valid limit                  18.0     True           False

*** Keywords ***
Flags Should Match Voltage
    [Arguments]    ${volts}    ${overvoltage}    ${undervoltage}
    Set Supply Voltage    ${volts}
    Get Frame Data    0x123
    Can Overvoltage Flag Should Be     ${overvoltage}
    Can Undervoltage Flag Should Be    ${undervoltage}