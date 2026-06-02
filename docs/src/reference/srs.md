# Software Requirements Specification (SRS)
## Project: MYCELIUM CORE

**Version:** 1.0
**Status:** Full SRS
**System Type:** Desktop sandbox application for modeling and auditing electronic voting on a local Ethereum network
**Architectural Model:** Single smart contract, local node, single GUI client

---

> **Implementation Note:** This SRS serves as the original baseline requirement document. The actual implementation differs in the following ways to improve architecture and UX:
>
> - **PyQt6** was chosen over PySide6 (see ADR-001).
> - The smart contract is named **`VotingCore.sol`** (instead of `VotingCoreSecure.sol`).
> - `session_manager.py` is not a standalone module — its logic is integrated directly into the `AppController` facade.
> - Data structures are grouped under `data/`: `data/chain-data/`, `data/logs/`, `data/exports/` (instead of root folders).

# 1. General Information

## 1.1 Name
**MYCELIUM CORE** — a simple autonomous desktop application for deploying a local blockchain environment, preparing a voting session, casting votes, viewing results, and conducting a basic security audit.

## 1.2 Purpose
The system is intended for:

- modeling secure on-chain voting;
- demonstrating the limitations and advantages of electronic voting on a smart contract;
- testing stage logic;
- demonstrating protection against double voting;
- conducting audit-oriented scenarios in a controlled environment.

## 1.3 Development Goal
Develop a compact, comprehensible, secure, and architecturally clean application that:

- uses **one smart contract** as the single source of truth;
- excludes a token-based voting model;
- does not allow direct blockchain logic in the UI;
- supports multiple voting sessions within a single application run;
- stores all required project files in a single root folder;
- supports localization and themes;
- remains convenient for subsequent maintenance.

## 1.4 System Character
The system is:

- educational;
- research-oriented;
- demonstrational;
- stand-alone (testbed);
- audit-oriented.

The system **is not intended** for use in real public or government elections.

## 1.5 Architecture Diagrams
For unambiguous understanding of component interactions, the system must be described by the following diagrams (the diagram document is delivered separately):

- **Component Diagram** – shows modules (GUI, Controller, Service Layer, Web3 Provider, Geth Manager, Nonce Manager) and the connections between them.
- **Sequence Diagram** for the "Create a New Session in Clean Mode" scenario – with steps: user confirmation, log archiving, Geth stop, chain-data cleanup, restart, new contract deployment.
- **State Diagram** for the voting session lifecycle: SETUP → ACTIVE → FINISHED → (archived).
- **Class Diagram** for core models (Election, Candidate, Voter, Session).

---

# 2. Core System Principles

1. **One contract — one truth.**
2. **Voting is performed only via the castVote method.**
3. **Critical constraints are enforced primarily on-chain.**
4. **The UI does not interact directly with Web3.**
5. **All write operations are performed only through the service layer.**
6. **The application must support the repeated creation of new voting sessions.**
7. **The system must be fully self-contained within a single project folder.**
8. **By default, the administrator's private key is not stored.**
9. **Light/dark theme and ru/en localization are mandatory.**
10. **Color semantics for statuses must be consistent.**

---

# 3. System Boundaries

## 3.1 What Is Included in the System
The system must provide:

- launching a local Geth node;
- checking RPC availability;
- compiling and deploying a single smart contract;
- registering candidates;
- registering voters in a whitelist;
- managing election stages;
- voter voting;
- generating a QR receipt;
- viewing results;
- auditing security invariants;
- exporting results;
- creating a new voting session;
- archiving the previous session;
- action logging;
- ru/en localization;
- light and dark themes.

## 3.2 What Is Not Included in the System
The system is not required to:

- provide anonymous cryptographic voting;
- use the public Ethereum mainnet/testnet;
- support a multi-user server backend;
- provide production-level security for real elections;
- implement tokens, mint, transfer, approve, allowance;
- use external databases.

---

# 4. Target Users

## 4.1 Administrator
Performs:

- contract deployment;
- adding candidates;
- adding voters;
- managing stages;
- starting a new session;
- exporting results.

## 4.2 Voter
Performs:

- entering a private key;
- selecting a candidate;
- submitting a vote;
- receiving a receipt.

## 4.3 Auditor / Tester
Performs:

- viewing results;
- verifying invariants;
- checking security statuses;
- analyzing logs and exported data.

---

# 5. Architectural Model

## 5.1 High-Level Scheme

```text
GUI (PySide6)
   ↓
Application Controller
   ↓
Service Layer
   ↓
Web3 / Compiler / Geth / Nonce Manager
   ↓
Voting smart contract
```

## 5.2 Architectural Constraints
The user interface layer must not:

- directly create Web3 contract instances;
- directly build transactions;
- directly sign transactions;
- directly call raw transaction send methods;
- contain voting business logic.

## 5.3 Mandatory System Layers
The system must be divided into at minimum:

- UI;
- controller;
- services;
- infrastructure;
- utils;
- contract artifacts.

---

# 6. Voting Session Model

## 6.1 Basic Requirement
The system must support **multiple voting sessions within a single application run**.

## 6.2 New Voting Session
A **"New Voting"** function must exist, launched from the UI.

## 6.3 Behavior When Starting a New Session
Before creating a new session, the system must:

- offer to save and archive the results of the current session;
- archive the current log;
- reset the interface's working context;
- clear the current contract addresses;
- clear the current local candidate and voter data from the active context.

## 6.4 New Session Modes
The system must support two modes:

### Fast Mode

- the current blockchain environment is preserved;
- a new contract is deployed;
- the previous session remains in the network history.

### Clean Mode

- the previous session is archived;
- the active blockchain environment is cleared;
- the local node is restarted;
- the new session begins on a clean chain.

**Clean Mode (detailed algorithm)**
When Clean Mode is selected, the system must perform the following steps strictly in order:

1. Request user confirmation with the warning: "All data from the current session will be archived; the blockchain will be completely deleted."
2. Archive the current log and results (if any) to `logs/archive/<session_id>/` and `exports/results/`.
3. Stop the Geth process (if running).
4. **Delete the `chain-data/active` folder entirely** (or rename it to `chain-data/archive/old_<timestamp>` for debugging purposes).
5. Recreate an empty `chain-data/active` folder.
6. Launch Geth with the initialization parameters for a new empty chain.
7. Wait for RPC readiness.
8. Reset the UI context (clear contract addresses, candidate/voter lists, etc.).
9. Return the interface to its initial state (SETUP stage, no contracts).

**Note:** After Clean Mode, previously deployed contracts and votes are completely lost. This corresponds to the behavior of "entirely new elections."

---

# 7. Project File Structure

## 7.1 General Requirement
All required project files must be located **in a single root folder**.

## 7.2 Target Structure

```text
mycelium-core/
│
├── main.py
├── requirements.txt
├── app.cfg
├── .env
├── .env.example
│
├── bin/
│   ├── geth.exe
│   └── solc.exe
│
├── contracts/
│   ├── VotingCoreSecure.sol
│   └── abi/
│       └── VotingCoreSecure.json
│
├── src/
│   ├── core/
│   │   ├── app_controller.py
│   │   ├── session_manager.py
│   │   ├── geth_manager.py
│   │   ├── compiler_service.py
│   │   ├── web3_provider.py
│   │   ├── nonce_manager.py
│   │   ├── voting_service.py
│   │   ├── audit_service.py
│   │   └── models.py
│   │
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── tabs/
│   │   │   ├── admin_tab.py
│   │   │   ├── vote_tab.py
│   │   │   └── audit_tab.py
│   │   │
│   │   ├── widgets/
│   │   │   ├── toast.py
│   │   │   ├── status_badge.py
│   │   │   ├── section_card.py
│   │   │   └── confirm_dialog.py
│   │   │
│   │   ├── themes/
│   │   │   ├── dark.qss
│   │   │   └── light.qss
│   │   │
│   │   └── i18n/
│   │       ├── ru.json
│   │       └── en.json
│   │
│   └── utils/
│       ├── config.py
│       ├── paths.py
│       ├── logger.py
│       ├── validators.py
│       ├── crypto.py
│       └── qr.py
│
├── chain-data/
│   ├── active/
│   └── archives/
│
├── logs/
│   ├── active/
│   │   └── session.log
│   └── archive/
│       └── <session_id>/
│
├── exports/
│   ├── voters/
│   ├── receipts/
│   └── results/
│
└── runtime/
    └── cache/
```

*Note: See the actual implemented structure in `src/development/setup.md` / `src/development/setup.ru.md`.*

**This is a template. The target structure may be modified.**

## 7.3 Requirements for the `bin/` Folder
The `bin/` folder must contain:

- a local `geth`;
- a local `solc` as an optional fallback.

The application must search for these binaries only within the project.

## 7.4 Requirements for the `contracts/` Folder
The contract and ABI artifacts must be located only in `bin/contracts/`.

## 7.5 Requirements for `chain-data/`
Blockchain data must be stored inside the project, not in OS system directories.

## 7.6 Requirements for `logs/`
Logs for current and past sessions must be located inside the project.

---

# 8. Project Configuration

## 8.1 User Config `app.cfg`
The `app.cfg` file is mandatory.

### It must store:

- selected language;
- selected theme;
- window size and position;
- last import/export paths;
- preferred new session mode;
- dev mode flag;
- other safe user settings.

### It must not store:

- voter private keys;
- the default administrator private key;
- sensitive secrets.

## 8.2 The `.env` File
The `.env` file is permitted and appropriate as a technical configuration file.

### It may contain:

- RPC host;
- RPC port;
- log level;
- dev mode flag;
- compiler options;
- gas defaults;
- optional dev admin key;
- other technical environment parameters that can be saved for reuse.

### It must not be used as the primary secure secrets storage.

## 8.3 Admin Private Key Storage
By default:

- the administrator's private key **must not be stored**.

Optionally:

- the system may support a **developer convenience mode**, in which the admin key is read from `.env`;
- in this case, the UI must explicitly indicate that insecure dev mode is active.

---

# 9. GUI Library Selection

## 9.1 Primary Recommendation
**PySide6** must be used for the project.

## 9.2 Rationale
PySide6 is suitable because:

- it supports desktop architecture well;
- it has a mature widget system;
- it supports QSS;
- it works well with tabs, tables, forms, and threads;
- it is suitable for cross-platform desktop development;
- it is convenient for long-term maintenance.

## 9.3 Acceptable Alternative
The use of PyQt6 is permitted if required for internal project reasons; however, PySide6 remains the preferred option.

---

# 10. Functional Requirements

## 10.1 Runtime Environment Management

### FR-ENV-01 Auto-start of Local Node
Upon application launch, the system must automatically start the local blockchain node from the `bin/` folder.

### FR-ENV-02 RPC Readiness Check
The system must verify RPC availability and transition to an operational state only after confirming node readiness.

### FR-ENV-03 RPC Status Display
The system must display the RPC connection status in the interface.

### FR-ENV-04 Block Number Display
The system must display the current block number.

### FR-ENV-05 Environment Error Handling
If the local node fails to start, the system must show the user a clear diagnostic message with the option to copy the error/message.

### FR-ENV-06 Graceful Node Shutdown
When the application is closed, the local node must be terminated gracefully/completely.

### FR-ENV-07 Unexpected Geth Termination Detection
The system must periodically (every 5 seconds) check whether the Geth process is alive. If the process is unresponsive or has terminated with an error, the UI must show a red status "🔴 RPC: GETH CRASHED" and block all operations that require writing to the blockchain.

### FR-ENV-08 Automatic Geth Restart
Upon a Geth crash, the system must offer the user the option to restart the node (a "Restart Node" button). Automatic restart without confirmation is not permitted, to prevent data loss.

### FR-ENV-09 "Address Already in Use" Error Handling
If the RPC port (default 8545) is occupied, the system must show an error on startup with a suggestion to change the port in `.env` and then exit.

### FR-ENV-10 RPC Connection Timeout
After starting Geth, the system must wait no more than 30 seconds for the RPC. If the RPC has not responded within this time, display the message: "Geth has started, but RPC is unavailable. Check Geth logs."

---

## 10.2 Compilation and Deployment

### FR-DEP-01 Single Contract Compilation
The system must compile one voting smart contract.

### FR-DEP-02 Deployment from the Interface
The administrator must be able to deploy the contract from the UI in a single operation.

### FR-DEP-03 Contract Address Display
After a successful deployment, the system must display the contract address.

### FR-DEP-04 ABI Storage
The contract ABI must be saved locally inside the project at `bin/contracts/abi`.

### FR-DEP-05 Session Context
After deployment, the contract address and related data must be saved in the context of the current session.

### FR-DEP-06 Accidental Redeployment Protection
The system must prevent accidental redeployment without a confirmed transition to a new session.

---

## 10.3 Election Configuration

### FR-CONF-01 Creating a New Election Configuration
The administrator must be able to specify:

- election name;
- session identifier;
- permissible candidate count limit.

### FR-CONF-02 Election Parameter Validation
The system must validate the election configuration before deployment.

---

## 10.4 Candidate Management

### FR-ADM-01 Adding Candidates
The administrator must be able to add candidates before voting begins.

### FR-ADM-02 Candidate Fields
The following must be specified for a candidate:

- name / full name;
- party / political affiliation;
- address.

### FR-ADM-03 Test Candidate Address Generation
The system must be able to generate a test candidate address.

### FR-ADM-04 Candidate Address Format Verification
The system must verify the correctness of the candidate address format.

### FR-ADM-05 Duplicate Prevention
The system must prevent adding a candidate with an already-existing address.

### FR-ADM-06 On-Chain Candidate Registration
The system must allow registering the prepared candidate list in the contract.

### FR-ADM-07 Stage Restriction
Candidate registration must be available only before voting starts.

---

## 10.5 Voter Management

### FR-ADM-08 Adding Voters to the Whitelist
The administrator must be able to add voters to the whitelist before voting begins.

### FR-ADM-09 Voter Sources
The system must support:

- manual address entry;
- import from JSON;
- test key generation.

### FR-ADM-10 Test Voter Generation
The system must be able to generate a specified number of test pairs:

- address;
- private key.

### FR-ADM-11 Voter JSON Export
The system must allow exporting test voter keys to JSON.

### FR-ADM-12 Export Risk Warning
Before exporting private keys, the system must display a high-importance warning.

### FR-ADM-13 On-Chain Whitelist Registration
The system must perform batch registration of voters in the whitelist.

### FR-ADM-14 Stage Restriction
Whitelist modifications must be available only before voting starts.

---

## 10.6 Stage Management

### FR-STAGE-01 Start Voting
The administrator must be able to transition the election to the active voting stage.

### FR-STAGE-02 End Voting
The administrator must be able to end voting.

### FR-STAGE-03 Stage-Based Operation Restriction
After voting starts, the system must prohibit changes to the setup portion.

### FR-STAGE-04 Stage Display
The current stage must be displayed in the UI at all times.

---

## 10.7 Voting

### FR-VOTE-01 Private Key Entry
The voter must be able to manually enter a private key.

### FR-VOTE-02 Load from JSON
The voter must be able to load a key from a JSON file.

### FR-VOTE-03 Address Computation
The system must automatically compute the address from the entered key.

### FR-VOTE-04 Voter Status Check
The system must display:

- whether the address is in the whitelist;
- whether the address has already voted;
- whether the voting stage is active.

### FR-VOTE-05 Candidate List Display
The system must display the list of registered candidates.

### FR-VOTE-06 Single Candidate Selection
The voter must be able to select only one candidate.

### FR-VOTE-07 Vote Submission
After selecting a candidate, the voter must be able to submit the vote.

### FR-VOTE-08 Repeat-Click Blocking
While a vote is being processed, the submit button must be disabled.

### FR-VOTE-09 Transaction Confirmation
After a successful vote submission, the system must display:

- TX Hash;
- block number;
- address of the selected candidate.

### FR-VOTE-10 Sensitive Data Clearing
After the operation is complete, the private key field must be cleared.

---

## 10.8 Receipt and Confirmation

### FR-REC-01 Receipt Generation
After a successful vote, the system must generate a receipt.

### FR-REC-02 QR Generation
The receipt must be available as a QR code.

### FR-REC-03 QR Saving
The user must be able to save the QR receipt.

### FR-REC-04 TX Hash Copying
The user must be able to copy the TX Hash.

---

## 10.9 Results

### FR-RES-01 Results Viewing
After voting ends, the system must display results by candidate.

### FR-RES-02 Results Sorting
Results must be sorted in descending order by vote count.

### FR-RES-03 Winner or Tie
The system must determine the winner or record a tie.

### FR-RES-04 Turnout
The system must calculate the voter turnout percentage.

### FR-RES-05 Results Export
The system must be able to export results to JSON.

---

## 10.10 Audit

### FR-AUD-01 Full Audit Launch
The system must launch a full audit of a completed voting session.

### FR-AUD-02 Double Voting Check
The system must verify that each voter voted no more than once.

### FR-AUD-03 Whitelist Check
The system must verify that only permitted addresses voted.

### FR-AUD-04 Stage Check
The system must verify that votes were cast only during the permitted stage.

### FR-AUD-05 Candidate Validity Check
The system must verify that votes were cast only for registered candidates.

### FR-AUD-06 Administration Constraint Check
The system must verify that administrative actions were performed only by the owner and only in permitted stages.

### FR-AUD-07 Audit Visual Representation
Audit results must be displayed as a clear status table.

### FR-AUD-08 Audit Report Export
The system must allow exporting a summary audit report.

---

## 10.11 New Voting Session

### FR-SESSION-01 Creating a New Session
The system must allow creating a new voting session without closing the application.

### FR-SESSION-02 Warning Before Reset
Before creating a new session, the system must request confirmation.

### FR-SESSION-03 Current Session Archiving
Before launching a new session, the system must offer to save results and archive the log.

### FR-SESSION-04 Fast Mode
The system must support creating a new session via a new deployment in the existing blockchain environment.

### FR-SESSION-05 Clean Mode
The system must support creating a new session with clearing of the blockchain environment and restarting the node.

### FR-SESSION-06 Active UI Context Reset
After a new session, the system must clear the previous session's active data from the interface.

---

## 10.12 Localization

### FR-I18N-01 Two-Language Support
The system must support at minimum:

- Russian;
- English.

### FR-I18N-02 JSON Localization
All user-facing texts must be stored in JSON files:

- `ru.json`
- `en.json`

### FR-I18N-03 Full Coverage
Localization must cover:

- tabs;
- buttons;
- statuses;
- tooltips;
- dialogs;
- errors;
- stage names;
- audit statuses;
- notifications.

### FR-I18N-04 Language Switching
The user must be able to change the language in the UI.

---

## 10.13 Theming

### FR-THEME-01 Light and Dark Theme
The system must support two themes:

- light;
- dark.

### FR-THEME-02 Selected Theme Persistence
The selected theme must be saved in `app.cfg`.

### FR-THEME-03 Application Without State Loss
Switching themes must not reset the current session.

---

# 11. Non-Functional Requirements

## 11.1 Architecture

### NFR-ARC-01 Single Smart Contract
The project must use only one voting smart contract.

### NFR-ARC-02 No Web3 Logic in UI
The UI must not work directly with Web3.

### NFR-ARC-03 Service Layer Is Mandatory
All blockchain operations must go through the services.

### NFR-ARC-04 Single Controller
A single coordinating application management layer must exist in the system.

### NFR-ARC-05 Modularity
The code must be divided into independent modules.

---

## 11.2 Security

### NFR-SEC-01 Do Not Store Admin Key by Default
The administrator's private key must not be saved automatically.

### NFR-SEC-02 Do Not Log Secrets
Secret data must not appear in logs.

### NFR-SEC-03 Minimize Key Lifetime in Memory
Keys must be kept in memory for as short a time as possible.

### NFR-SEC-04 Centralized Nonce Manager
All write operations must use a single nonce manager.

### NFR-SEC-05 Secure Default Behavior
Insufficiently confirmed states must be treated as prohibiting the execution of an action.

### NFR-SEC-06 On-Chain Constraint Priority
Primary constraints must be enforced by the contract.

### NFR-SEC-07 Dev Mode Must Be Clearly Marked
If the admin key from `.env` is in use, the UI must display the developer mode indication and a warning about its insecurity.

---

## 11.3 Performance

### NFR-PERF-01 Non-Blocking Interface
Long-running operations must not block the UI.

### NFR-PERF-02 Background Worker Tasks
Compilation, deployment, batch operations, and audit must run in background tasks.

### NFR-PERF-03 Operation Progress
Progress or activity indicators must be displayed for long-running operations.

---

## 11.4 Reliability

### NFR-REL-01 RPC Error Resilience
The system must correctly handle temporary RPC unavailability.

### NFR-REL-02 Input Error Resilience
Invalid addresses, keys, and files must not cause an application crash.

### NFR-REL-03 Controlled Shutdown
When the application is closed, background processes must be terminated gracefully.

### NFR-REL-04 Safe New Session Handling
The transition to a new session must not result in a partially reset state.

---

## 11.5 Maintainability

### NFR-MNT-01 Clear Project Structure
The directory structure must be logical and straightforward.

### NFR-MNT-02 Minimization of Duplication
Duplication of logic between layers is not permitted.

### NFR-MNT-03 Interface Editability
Changing the UI must not require changing backend logic.

### NFR-MNT-04 Texts Moved to JSON
All texts must be stored in localization files.

### NFR-MNT-05 Themes Moved to Separate Files
Theming must be implemented through separate QSS files.

---

## 11.6 Observability

### NFR-OBS-01 Key Action Logging
All important actions must be written to the session log.

### NFR-OBS-02 Session Log Archiving
Logs of completed sessions must be archived.

### NFR-OBS-03 Error and Exception Logging
Errors and exceptions must be logged.

---

## 11.7 Portability

### NFR-PORT-01 All Project Resources Within One Folder
Binaries, contracts, configs, styles, and localization must be inside the project.

### NFR-PORT-02 Minimal Manual Configuration
The application must be ready to run after installing dependencies without complex manual configuration.

---

# 12. UI Color Semantics Requirements

## 12.1 General Color Logic

### 🟢 Green
Used for:

- successful state;
- confirmed connection;
- valid input;
- successful transaction;
- Passed in audit;
- permitted status;
- active readiness.

### 🟡 Yellow
Used for:

- warnings;
- Setup stage;
- incomplete configuration;
- informational warnings;
- user attention;
- tie;
- dev mode warning.

### 🔴 Red
Used for:

- errors;
- prohibited actions;
- invalid input;
- disconnected RPC;
- Failed in audit;
- Finished stage as a final closed state;
- critical security warnings.

## 12.2 Accessibility Requirement
Color must not be the sole indicator of meaning.
Alongside color, the following must always be present:

- text;
- and/or an icon;
- and/or a status label.

---

# 13. ASCII UI Visualization (example)

## 13.1 Main Window

```text
+--------------------------------------------------------------------------------------------------+
| MYCELIUM CORE                            RPC: [🟢 CONNECTED] | Block: 1054 | Theme: Dark         |
+--------------------------------------------------------------------------------------------------+
| [ Admin ] [ Vote ] [ Audit ]                                                    [ New Session ]  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|                                         ACTIVE TAB CONTENT                                       |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
| Stage: [🟡 SETUP] | Contract: 0x............................................. | Lang: RU         |
+--------------------------------------------------------------------------------------------------+
```

## 13.2 Admin Tab

```text
+--------------------------------------------------------------------------------------------------+
| ADMIN                                                                                            |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Election --------------------------------------------------------+
| Title:        [ Local Secure Election 2026                                ]                      |
| Election ID:  [ auto-generated                                            ]                      |
| Max Cands:    [ 10 ]                                                                             |
| Admin Key:    [ ******************************************************* ] [Show]                 |
|                                                                                                  |
| [ Deploy Election ]                                                                              |
| Contract: 0x............................................................ (green/yellow/red color)|
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Candidates ------------------------------------------------------+
| Name:   [ Alice Johnson                           ]                                              |
| Party:  [ Reform Alliance                         ]                                              |
| Addr:   [ 0x......................................................... ] [Gen] [Add]              |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | Name                  | Party                | Address                                       | |
| +----------------------------------------------------------------------------------------------+ |
| | Alice Johnson         | Reform Alliance      | 0x...                                         | |
| | Bob Smith             | Civic Front          | 0x...                                         | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| [ Register Candidates ]                                                                          |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Voters ----------------------------------------------------------+
| [ Generate Test Voters ] Count: [ 100 ]                                                          |
| [ Import JSON ] [ Export JSON ]                                                                  |
| Loaded voters: 100                                                                               |
|                                                                                                  |
| [ Add Voters To Whitelist ]                                                                      |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Stage -----------------------------------------------------------+
| Current Stage: [🟡 SETUP]                                                                        |
| [ Start Voting ]                                                           [ Finish Voting ]     |
+--------------------------------------------------------------------------------------------------+
```

## 13.3 Vote Tab

```text
+--------------------------------------------------------------------------------------------------+
| VOTE                                                                                             |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Authentication --------------------------------------------------+
| Private Key: [ ******************************************************* ] [Show] [Load JSON]      |
| Address:      0x........................................................................         |
| Whitelisted:  [🟢 YES]                                                                           |
| Has Voted:    [🟡 NO]                                                                            |
| Stage:        [🟢 ACTIVE]                                                                        |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Candidates ------------------------------------------------------+
| ( ) Alice Johnson      | Reform Alliance                                                         |
| ( ) Bob Smith          | Civic Front                                                             |
| ( ) Carol Lee          | Green Horizon                                                           |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Voting ----------------------------------------------------------+
|                           [ CAST SECURE VOTE ]                                                   |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Receipt ---------------------------------------------------------+
|                                                                                                  |
|                                                                                                  |
|                              +----------------------------+                                      |
|                              |                            |                                      |
|                              |         QR RECEIPT         |                                      |
|                              |                            |                                      |
|                              +----------------------------+                                      |
|                                                                                                  |
| TX Hash: 0x......................................................................................|
|                                                                                                  |
|  [ Save QR ] [ Copy TX ]                                                                         |
+--------------------------------------------------------------------------------------------------+
```

## 13.4 Audit Tab

```text
+--------------------------------------------------------------------------------------------------+
| AUDIT                                                                                            |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Results ---------------------------------------------------------+
| Stage:        [🔴 FINISHED]                                                                      |
| Total Voters: 100                                                                                |
| Total Votes:  87                                                                                 |
| Turnout:      87%                                                                                |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | Candidate              | Party                | Address                   | Votes            | |
| +----------------------------------------------------------------------------------------------+ |
| | Alice Johnson          | Reform Alliance      | 0x...                     | 41               | |
| | Bob Smith              | Civic Front          | 0x...                     | 29               | |
| | Carol Lee              | Green Horizon        | 0x...                     | 17               | |
| +----------------------------------------------------------------------------------------------+ |
|                                                                                                  |
| Winner: Alice Johnson                                                                            |
| [ Export Results ]                                                                               |
+--------------------------------------------------------------------------------------------------+

+-------------------------------- Security Audit --------------------------------------------------+
| [ Run Full Audit ]                                                                               |
|                                                                                                  |
| +----------------------------------------------------------------------------------------------+ |
| | Check                                 | Status        | Details                              | |
| +----------------------------------------------------------------------------------------------+ |
| | Double Vote Protection                | [🟢 PASSED]   | No duplicate voters                  | |
| | Whitelist Enforcement                 | [🟢 PASSED]   | All voters whitelisted               | |
| | Stage Enforcement                     | [🟢 PASSED]   | Votes cast only in Active            | |
| | Candidate Integrity                   | [🟢 PASSED]   | All votes target valid candidates    | |
| | Owner-only Administration             | [🟢 PASSED]   | Restricted operations protected      | |
| | Post-start Freeze                     | [🟢 PASSED]   | Setup locked after start             | |
| +----------------------------------------------------------------------------------------------+ |
+--------------------------------------------------------------------------------------------------+
```

## 13.5 Error and Warning Examples

```text
RPC Status:        [🔴 DISCONNECTED]
Private Key:       [ bad_input ]                  [🔴 INVALID]
Export Secret Keys:[ voters.json ]                [🟡 WARNING]
Deploy Result:     [ contract deployed ]          [🟢 SUCCESS]
```

---

# 14. Localization Requirements

## 14.1 Localization Files
The following files are mandatory:

- `src/ui/i18n/ru.json`
- `src/ui/i18n/en.json`

## 14.2 What Is Subject to Localization
All user-facing texts:

- menus;
- tabs;
- fields;
- buttons;
- dialogs;
- statuses;
- notifications;
- errors;
- tooltips;
- audit stages;
- stage names;
- color statuses.

## 14.3 Behavior
At application startup, the language must be loaded from `app.cfg`.

---

# 15. Theme Requirements

## 15.1 Theme Files
The following are mandatory:

- `src/ui/themes/dark.qss`
- `src/ui/themes/light.qss`

## 15.2 Behavior
The selected theme must:

- be loaded from `app.cfg`;
- be applied to the entire application;
- be changeable without resetting the active session.

---

# 16. Data Formats for Export and Import

## 16.1 Voter Export (voters.json)
Upon export per FR-ADM-11, a JSON of the following structure is generated. Example:
```json
{
  "election_id": "SESSION_20260423_001",
  "export_timestamp": "2026-04-23T14:35:00Z",
  "voters": [
    {
      "address": "0xAbC...123",
      "private_key": "0x...",
      "has_voted": false
    }
  ]
}
```

A warning must be displayed before export (FR-ADM-12).

## 16.2 Results Export (results.json)
Upon export per FR-RES-05, a JSON is generated. Example:
```json
{
  "election": {
    "title": "Local Secure Election 2026",
    "session_id": "SESSION_20260423_001",
    "stage": "FINISHED",
    "start_block": 1024,
    "end_block": 2048
  },
  "statistics": {
    "total_voters": 100,
    "total_votes": 87,
    "turnout_percent": 87.0
  },
  "results": [
    {
      "candidate_name": "Alice Johnson",
      "party": "Reform Alliance",
      "address": "0x...",
      "votes": 41
    }
  ],
  "winner": "Alice Johnson",
  "is_tie": false
}
```

## 16.3 Audit Report Export (audit_report.json)
Additionally (FR-AUD-08), a report must be exported. Example:
```json
{
  "session_id": "...",
  "audit_timestamp": "...",
  "checks": [
    {
      "check_name": "Double Vote Protection",
      "status": "PASSED",
      "details": "No duplicate voters"
    }
  ]
}
```

---

# 17. Logging Requirements

## 17.1 Current Session Log
The system must maintain an active log at:
```text
logs/active/session.log
```

## 17.2 Archiving
Upon session completion or archiving, the log must be moved to the archive.

## 17.3 What Must Be Logged

- Geth start/stop;
- compilation;
- deployment;
- candidate registration;
- voter registration;
- stage changes;
- vote submission;
- new session creation;
- audit launch;
- results export;
- errors;
- unhandled exceptions.

## 17.4 Prohibition on Logging Secrets
Private keys, seed phrases, and similar secrets must not appear in the log.

---

# 18. Acceptance Criteria

The system is considered accepted if the following conditions are met:

1. All project resources are located in a single root folder.
2. Local Geth starts automatically from `bin/`.
3. The contract is compiled and deployed from the UI.
4. A single smart contract is used.
5. The administrator can register candidates.
6. The administrator can register the voter whitelist.
7. Voting can only be started after the election is prepared.
8. A voter can vote only once.
9. Voting is impossible outside of the active stage.
10. Voting is impossible from outside the whitelist.
11. After voting, the TX Hash and QR receipt are displayed.
12. After the election ends, correct results are displayed.
13. The audit shows the statuses of security invariants.
14. ru/en localization is supported via JSON.
15. dark/light themes are supported.
16. The selected language and theme are saved in `app.cfg`.
17. The admin key is not stored by default.
18. Dev mode with a key from `.env` is explicitly marked as insecure.
19. The system supports "New Voting."
20. Fast and Clean modes for new sessions are available.
21. Logs and results from past sessions are archived.
22. The UI contains no direct Web3 operations.
23. Long-running operations do not block the interface.

---

# 19. Development Stages

## Stage 1. Basic Infrastructure and Project Skeleton
Includes:

- creating the directory structure;
- selecting PySide6;
- connecting the `app.cfg` configuration;
- connecting `.env`;
- setting up logging;
- implementing local Geth start and stop;
- creating the basic application window;
- connecting themes and localization.

## Stage 2. Smart Contract and Service Layer
Includes:

- implementing a single voting smart contract;
- compilation and deployment;
- implementing the Web3 provider;
- implementing the nonce manager;
- implementing the service layer;
- implementing the app controller.

## Stage 3. Administrator Screen and Election Preparation
Includes:

- election configuration;
- adding candidates;
- generating and importing voters;
- JSON export with warning;
- whitelist registration;
- stage management;
- status display.

## Stage 4. Voting Screen and Receipts
Includes:

- entering and loading a private key;
- checking voter status;
- displaying candidates;
- vote submission;
- clearing sensitive data;
- generating TX Hash and QR receipt.

## Stage 5. Audit, New Sessions, and Final Stabilization
Includes:

- results screen;
- calculating turnout and winner;
- security audit;
- results export;
- implementing "New Voting";
- Fast and Clean new session modes;
- archiving logs and results;
- final debugging and acceptance testing.

---

# 20. Final Product Requirement

The result of development must be a compact, self-contained, secure, and maintainable desktop project that:

- runs from a single root folder;
- uses one smart contract;
- contains no superfluous token logic;
- enables conducting multiple voting sessions;
- supports themes and localization;
- is suitable for demonstration, education, and auditing of secure on-chain voting.

---

## 20. Version Management and Data Migration

### 20.1 Application Versioning
Each release must have a semantic version in the form `MAJOR.MINOR.PATCH` (e.g., `1.0.0`). The version is displayed in the "About" window and written to `app.cfg` and the log at startup.

### 20.2 Configuration Compatibility
When a new version starts, the system must check the version in `app.cfg`. If the file is absent or the version is outdated, the system must create a backup of the old config and generate a new one with default settings. Loss of user theme/language settings is not acceptable.

### 20.3 Smart Contract ABI Migration
Since the contract is updated only through deployment in a new session, data migration is not required. However, the application code must provide the ability to specify in `.env` the expected ABI version (hash). If the ABI of the deployed contract does not match the expected one, the application must show a warning.

### 20.4 Archiving Old Sessions
When a new session is created (in any mode), the system must not automatically delete archives older than 30 days. Deletion is only by an explicit administrator action through the UI or manually.