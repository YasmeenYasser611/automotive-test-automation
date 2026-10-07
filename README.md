# Automotive Robot Framework Test Automation

## Project Overview

**Automotive Robot Framework Test Automation** is a simulation-based automotive test-automation project designed to demonstrate a **black-box testing approach** using **Robot Framework** and a reusable **Python automation library**.

The project models an ECU's externally observable behavior and automates its verification through Robot Framework test cases.

The main focus is not testing the ECU's internal implementation. Instead, the tests are derived from the expected behavior of the system:

```text
Requirement / Expected ECU Behavior
                |
                v
        Black-Box Test Design
                |
        +-------+-------+
        |               |
        v               v
Equivalence         Boundary Value
Partitioning         Analysis (BVA)
        |               |
        +-------+-------+
                |
                v
          Test Cases
                |
                v
        Robot Framework
                |
                v
       Python Test Library
                |
                v
        ECU Simulation
                |
                v
          PASS / FAIL
```

The ECU and bench interaction are simulated in Python. This allows the project to demonstrate the test-automation architecture without requiring physical automotive hardware.

---

# Project Purpose

The project demonstrates practical concepts used in an automotive test-automation environment, especially:

- Black-box testing
- Equivalence Partitioning (EP)
- Boundary Value Analysis (BVA)
- Robot Framework automation
- Python reusable/shared test libraries
- Positive and negative testing
- Exception handling
- Retry mechanisms
- CAN frame validation
- CAN status-bit / bitmask validation
- Test reporting
- CI/CD-ready test execution

The project is intentionally structured around the workflow:

```text
Test Requirement
      ↓
Test Design
      ↓
Robot Framework Test
      ↓
Python Automation Library
      ↓
ECU / Bench Simulation
      ↓
Observable Result
      ↓
PASS / FAIL
```

---

# Black-Box Testing Approach

The voltage tests are designed from the **external behavior of the ECU**, rather than its internal implementation.

The tester does not need to know how the ECU internally calculates its voltage state.

The important question is:

> Given a voltage input, what behavior should be observable from the ECU?

For example:

```text
Input:  7.0 V
Expected external behavior: UNDERVOLTAGE
```

The test then compares the observed result with the expected result.

This makes the voltage test suite a **black-box test**.

The Python ECU model is only a stand-in for the real ECU/bench interface. In a real environment, the same Robot Framework test concept could interact with physical hardware instead.

---

# Test Design: Equivalence Partitioning + BVA

The 14 voltage test cases are **not only BVA tests**.

They combine:

- **Equivalence Partitioning (EP)** to divide the input space into groups of values expected to produce the same behavior.
- **Boundary Value Analysis (BVA)** to test values at and around the transitions between those groups.

## Equivalence Partitions

Based on the assumptions used in this project, the voltage domain is divided into these behavioral partitions:

```text
Voltage
│
├── V < 5 V
│      → UNSAFE / rejected
│
├── 5 V ≤ V < 9 V
│      → UNDERVOLTAGE
│
├── 9 V ≤ V ≤ 14 V
│      → NORMAL
│
├── 14 V < V ≤ 18 V
│      → OVERVOLTAGE
│
└── V > 18 V
       → UNSAFE / rejected
```

These partitions allow representative values to be selected instead of testing every possible voltage.

## Boundary Value Analysis

BVA is then applied around important transitions:

```text
5.0
9.0
14.0
18.0
```

Values immediately around the boundaries are also tested:

```text
8.9 → UNDERVOLTAGE
9.0 → NORMAL
9.1 → NORMAL

13.9 → NORMAL
14.0 → NORMAL
14.1 → OVERVOLTAGE

17.9 → OVERVOLTAGE
18.0 → OVERVOLTAGE
```

This gives coverage of both the **equivalence classes** and their **boundaries**.

> The voltage limits in this project are assumptions used for the simulation and should be confirmed against the actual ECU requirements in a real project.

---

# Voltage Test Cases

The voltage suite contains **TC01–TC14**.

| TC | Voltage | Expected Behavior | Test Design |
|---|---:|---|---|
| TC01 | 5.0 V | UNDERVOLTAGE | Boundary |
| TC02 | 5.1 V | UNDERVOLTAGE | Just inside partition |
| TC03 | 7.0 V | UNDERVOLTAGE | Equivalence partition representative |
| TC04 | 8.9 V | UNDERVOLTAGE | Boundary |
| TC05 | 9.0 V | NORMAL | Boundary |
| TC06 | 9.1 V | NORMAL | Just inside partition |
| TC07 | 11.5 V | NORMAL | Equivalence partition representative |
| TC08 | 13.9 V | NORMAL | Boundary |
| TC09 | 14.0 V | NORMAL | Boundary |
| TC10 | 14.1 V | OVERVOLTAGE | Boundary |
| TC11 | 16.0 V | OVERVOLTAGE | Equivalence partition representative |
| TC12 | 17.9 V | OVERVOLTAGE | Boundary |
| TC13 | 18.0 V | OVERVOLTAGE | Boundary |
| TC14 | 4.9 V / 18.1 V | UNSAFE / Rejected | Invalid partitions |

The suite uses Robot Framework's **Test Template** to execute the same behavioral check with different voltage inputs and expected results.

---

# 1. Voltage Behavior Testing

The main Robot Framework voltage test uses:

```robot
*** Settings ***
Test Template    Check ECU Behaviour
```

The common test logic is:

```robot
Check ECU Behaviour
    [Arguments]    ${volts}    ${expected}
    ${actual}=    ECU Model Reacts To    ${volts}
    Should Be Equal    ${actual}    ${expected}
```

This separates:

```text
Test Data
    +
Test Logic
```

The test data represents different equivalence partitions and boundary conditions.

---

# 2. CAN Testing

The CAN test suite contains **6 test cases**.

It validates:

- Valid CAN frame
- Invalid CAN ID
- DLC mismatch
- Overvoltage status flag
- Undervoltage status flag
- Clear status flags

Example:

```text
CAN ID : 0x123
DLC    : 4
DATA   : 11 22 33 00
```

The Python library validates:

- Standard CAN ID range
- DLC range
- Number of data bytes
- Data-byte range

---

## Voltage to CAN Flag Testing

`tests/voltage_flags_tests.robot` follows the same flow as a bench test:

```text
Set Supply Voltage  ->  Get Frame Data (0x123)  ->  check the flags in Byte 4
```

The simulated bench returns frame `0x123` for the current supply voltage. The Robot test then checks the overvoltage and undervoltage flags with the bit masks below. It uses the same 13 voltage points as the voltage suite, so each voltage is checked both as an ECU behaviour and as a flag in the CAN frame.

---

## CAN Bitmask Validation

The project also demonstrates checking ECU status flags using bitwise operations.

Example:

```python
actual = (byte4 & mask) != 0
```

The simulated status byte uses:

```text
Overvoltage flag  → 0x02
Undervoltage flag → 0x10
```

> **Note:** `0x02` for Bit 1 counts bits from 0, while `0x10` for Bit 5 counts from 1. In a real project, the bit numbering should be confirmed with the requirements engineer before relying on these masks.

This represents a common embedded/automotive testing concept where multiple status signals are packed into a single byte.

---

# 3. Exception Handling

The Python automation library demonstrates **specific exception handling** rather than using a broad bare `except:`.

Example:

```python
try:
    ...
except ConnectionError as error:
    raise ECUCommunicationError(
        f"Failed to communicate with ECU: {error}"
    ) from error
```

The purpose is to:

1. Catch the expected communication failure.
2. Convert it into a meaningful automation-level exception.
3. Preserve the original exception as the cause.
4. Allow Robot Framework to report a clear test failure.

This is especially important for a reusable/shared automation library because silently swallowing exceptions can hide real automation problems.

---

# 4. Retry Mechanism

The project demonstrates recovery from temporary ECU communication failures.

Conceptually:

```text
Attempt 1
   |
   X Communication failure
   |
   v
 Wait
   |
   v
Attempt 2
   |
   X Communication failure
   |
   v
 Wait
   |
   v
Attempt 3
   |
   v
 Success
```

If communication succeeds, the function returns immediately.

If every attempt fails, the final meaningful communication exception is raised.

Robot Framework verifies both scenarios:

- Communication eventually succeeds after retry.
- All retry attempts fail.

---

# 5. Negative Testing

The project does not test only successful scenarios.

Negative tests verify that invalid conditions are handled correctly.

Examples include:

- Invalid CAN ID
- Incorrect DLC
- ECU communication failure
- Invalid retry count
- Unsafe voltage

Robot Framework uses:

```robot
Run Keyword And Expect Error
```

to verify expected failures.

For example:

```robot
Run Keyword And Expect Error
...    *UNSAFE*
...    ECU Model Reacts To    4.9
```

This makes failure behavior part of the automated specification.

---

# 6. Robot Framework + Python Library

The project demonstrates a reusable Python library consumed by Robot Framework.

Architecture:

```text
Robot Framework
       |
       | Robot keyword
       v
AutomotiveLibrary.py
       |
       | automation logic
       v
ECU / CAN / Communication Simulation
```

This approach is useful for shared automation libraries because common functionality can be implemented once in Python and reused by many Robot Framework test suites.

---

# 7. Jenkins CI/CD

The project is integrated with **Jenkins** to execute the Robot Framework test suite as part of a CI/CD workflow.

The Jenkins pipeline is defined in the root-level `Jenkinsfile`.

The pipeline follows this flow:

```text
GitHub Repository
       |
       v
Jenkins Pipeline
       |
       v
Checkout source code
       |
       v
Setup Python virtual environment
       |
       v
Install project dependencies
       |
       v
Run Robot Framework
       |
       v
Publish Robot Framework results
       |
       v
Archive test artifacts
```

## Jenkins Pipeline

The pipeline performs three main stages:

### Setup

Jenkins creates a Python virtual environment and installs the dependencies defined by the project.

```groovy
stage('Setup') {
    steps {
        sh '''
            python3 -m venv venv
            venv/bin/python -m pip install --upgrade pip
            venv/bin/python -m pip install -r requirements.txt
        '''
    }
}
```

### Test

Jenkins executes the complete Robot Framework test suite:

```bash
venv/bin/python -m robot --outputdir tests/results tests/
```

This runs all voltage, CAN, and exception/retry test suites.

### Post

After the test execution, Jenkins publishes the Robot Framework results and archives the generated reports:

```text
results/
├── output.xml
├── log.html
└── report.html
```

This makes the automated test results available directly from the Jenkins build.

## Jenkins Build Result

After every build, Jenkins shows the Robot Framework result on the build page (passed and failed tests per suite) and archives the reports:

```text
results/
├── output.xml
├── log.html
└── report.html
```

This demonstrates the complete CI/CD path:

```text
GitHub
   ↓
Jenkins
   ↓
Python Environment
   ↓
Robot Framework
   ↓
Automated Tests
   ↓
Robot Report
   ↓
PASS / FAIL
```

## GitHub Actions

The repository also contains a GitHub Actions workflow (`.github/workflows/robot-tests.yml`). On every push and pull request it installs the dependencies, runs the same Robot Framework suite, and uploads the reports as a build artifact.

---

# 8. Project Structure

```text
automotive-test-automation/
|
├── libraries/
│   └── AutomotiveLibrary.py
|
├── resources/
│   └── common.resource
|
├── tests/
│   ├── voltage_tests.robot
│   ├── voltage_flags_tests.robot
│   ├── can_tests.robot
│   └── exception_retry_tests.robot
|
├── .github/
│   └── workflows/
│       └── robot-tests.yml
|
├── Jenkinsfile
├── requirements.txt
├── README.md
└── .gitignore
```

### `libraries/AutomotiveLibrary.py`

Contains reusable Python keywords for:

- ECU voltage behavior
- Voltage validation
- CAN frame validation
- CAN flag validation
- Communication simulation
- Exception handling
- Retry logic

### `resources/common.resource`

Loads the Python automation library for Robot Framework suites.

### `tests/`

Contains the automated Robot Framework test suites:

- `voltage_tests.robot`: ECU behaviour at each voltage (EP + BVA)
- `voltage_flags_tests.robot`: the same voltages checked as flags in CAN frame `0x123`
- `can_tests.robot`: CAN frame and status-flag validation
- `exception_retry_tests.robot`: communication failure and retry

---

# 9. Test Coverage

The project currently contains **38 automated test cases**.

| Test Area | Test Cases | Purpose |
|---|---:|---|
| Voltage Behavior | 14 | EP + BVA + positive/negative behavior testing |
| Voltage to CAN flags | 13 | Same voltages checked as flags in frame 0x123 |
| CAN | 6 | CAN frame and status-flag validation |
| Exception & Retry | 5 | Communication failure and recovery |
| **Total** | **38** | **38/38 PASS** |

Latest local execution:

```text
38 tests, 38 passed, 0 failed
```

---





# Project Status

**Status: Functional**

```text
38 automated tests
38 passed
0 failed
```

The current version is a **simulation-based portfolio project** focused on black-box test design, Robot Framework/Python automation, and Jenkins CI/CD.

---

