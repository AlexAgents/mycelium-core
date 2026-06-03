# User Stories & Acceptance Criteria

Key user stories for **MYCELIUM CORE**, grouped by actor.
Each story includes acceptance criteria in Given/When/Then format.

Full requirements traceability: [SRS](./srs.md) | [ADR](../architecture/overview.md)

---

## Administrator Stories

### US-ADM-01: Deploy Voting Contract

**As** an Administrator,
**I want** to deploy a new VotingCore contract from the UI,
**So that** I can start preparing a new election session.

**Acceptance Criteria:**

```gherkin
Given the admin private key is entered and valid
  And the Geth node is connected (RPC status CONNECTED)
When I click "Deploy VotingCore"
Then the contract is compiled and deployed to the local chain
  And the contract address is displayed in the footer
  And the Deploy button becomes disabled
  And the admin key field becomes read-only
  And a success toast "Contract deployed" is shown
```

**Related:** FR-DEP-01, FR-DEP-02, FR-DEP-06, ADR-004

---

### US-ADM-02: Register Candidates

**As** an Administrator,
**I want** to add candidates locally and register them on-chain in one batch,
**So that** voters can select from the registered list.

**Acceptance Criteria:**

```gherkin
Given at least 2 candidates are added to the staging table
  And admin key is entered
When I click "Register On-Chain"
Then each candidate is registered via addCandidate() transaction
  And the candidate input fields become disabled
  And the Vote tab auto-loads the candidate list
  And a toast shows the number of registered candidates
```

```gherkin
Given only 1 candidate is in the staging table
When I click "Register On-Chain"
Then a warning dialog "At least 2 candidates required" is shown
  And no transaction is sent
```

**Related:** FR-ADM-01, FR-ADM-06, FR-ADM-07

---

### US-ADM-03: Generate and Whitelist Voters

**As** an Administrator,
**I want** to generate test voters, fund them, and add to whitelist,
**So that** they can participate in voting.

**Acceptance Criteria:**

```gherkin
Given the contract is deployed
  And I set count to 10
When I click "Generate"
Then 10 key pairs are created
  And the "Loaded" counter shows 10
```

```gherkin
Given 10 voters are generated
  And admin key is entered
When I click "Fund" with 0.01 ETH
Then a confirmation dialog shows total amount
  And after confirmation each voter receives 0.01 ETH
  And the "Funded" counter updates
```

```gherkin
Given voters are generated and funded
When I click "Add Voters To Whitelist"
Then all addresses are registered on-chain via addVotersBatch()
  And the "Whitelisted" counter updates
```

**Related:** FR-ADM-08, FR-ADM-10, FR-ADM-13

---

### US-ADM-04: Start and Finish Voting

**As** an Administrator,
**I want** to control the voting lifecycle stages,
**So that** the election proceeds in the correct order.

**Acceptance Criteria:**

```gherkin
Given the contract is in SETUP stage
  And at least 2 candidates are registered
  And whitelist is not empty
When I click "Start Voting"
Then the stage changes to ACTIVE
  And the Vote tab becomes functional
  And the Start button becomes disabled
```

```gherkin
Given the contract is in ACTIVE stage
When I click "Finish Voting"
Then the stage changes to FINISHED
  And no new votes can be cast
  And Full/Final audit modes become available
```

```gherkin
Given the contract is in SETUP
  And whitelist is empty
When I click "Start Voting"
Then a warning "Whitelist is empty" is shown
  And voting does not start
```

**Related:** FR-STAGE-01, FR-STAGE-02, FR-STAGE-03, ADR-004

---

## Voter Stories

### US-VOT-01: Cast a Vote

**As** a Voter,
**I want** to authenticate with my private key and vote for a candidate,
**So that** my choice is recorded on the blockchain.

**Acceptance Criteria:**

```gherkin
Given I enter a valid private key
  And voting stage is ACTIVE
  And I am in the whitelist
  And I have not voted yet
  And I have sufficient ETH for gas
When I select a candidate and click "CAST VOTE"
Then a vote transaction is submitted
  And the TX hash and QR receipt are displayed
  And the private key field is cleared
  And a success toast is shown
```

```gherkin
Given I enter a valid private key
  And I have already voted
When I click "CAST VOTE"
Then a warning "This address has already voted" is shown
  And no transaction is sent
```

```gherkin
Given I enter a valid private key
  And voting stage is FINISHED
When I attempt to vote
Then a dialog "Voting has already finished" is shown
```

**Related:** FR-VOTE-01 through FR-VOTE-10, FR-REC-01 through FR-REC-04

---

### US-VOT-02: Mass Vote for Testing

**As** a Tester,
**I want** to cast random votes for all voters automatically,
**So that** I can generate test data for audit demonstrations.

**Acceptance Criteria:**

```gherkin
Given voting is ACTIVE
  And I have a JSON file with voter keys
When I click "From JSON File" and confirm
Then each voter is checked: key valid, whitelisted, not voted, balance OK
  And eligible voters cast a random vote
  And ineligible voters are skipped with reason logged
  And a summary toast shows voted/skipped/failed counts
  And one voter failure does not stop the entire process
```

**Related:** FR-VOTE-07, NFR-PERF-02

---

## Auditor Stories

### US-AUD-01: Run Full Security Audit

**As** an Auditor,
**I want** to run all security checks after voting finishes,
**So that** I can verify election integrity.

**Acceptance Criteria:**

```gherkin
Given voting stage is FINISHED
When I select "Full Audit" and click "Run Audit"
Then all 6 SEC-checks are executed
  And results appear in the checks table with PASSED/FAILED/WARNING status
  And the results table shows vote counts per candidate
  And the winner is determined
  And export buttons (Copy/JSON/CSV) become enabled
```

```gherkin
Given voting stage is SETUP
When I try to select "Full Audit"
Then the mode shows "(unavailable)" and Run Audit is disabled
```

**Related:** FR-AUD-01 through FR-AUD-08

---

### US-AUD-02: Export Audit Report

**As** an Auditor,
**I want** to export the complete audit report,
**So that** I have an immutable record for archival.

**Acceptance Criteria:**

```gherkin
Given an audit has been run successfully
When I click "JSON"
Then a file dialog opens
  And the full report (results + audit checks + winner) is saved
  And a success toast is shown
```

```gherkin
Given an audit has been run
When I click "Copy Report"
Then the full JSON report is copied to clipboard
```

**Related:** FR-AUD-08, FR-RES-05

---

## Cross-Cutting Stories

### US-SYS-01: New Voting Session

**As** an Administrator,
**I want** to start a fresh session without restarting the app,
**So that** I can conduct multiple elections in one run.

**Acceptance Criteria:**

```gherkin
Given a session is active with deployed contract
When I click "New Session" and confirm
Then the current log is archived
  And all tabs are reset to initial state
  And a new session UUID is generated
  And the contract address shows "not deployed"
  And the stage resets to SETUP
```

**Related:** FR-SESSION-01 through FR-SESSION-06, ADR-004

---

### US-SYS-02: Language Switch

**As** a User,
**I want** to switch interface language without restarting,
**So that** I can use the app in my preferred language.

**Acceptance Criteria:**

```gherkin
Given the interface is in English
When I select "RU" from the language combo
Then all labels, buttons, and dialogs update to Russian
  And a toast warns that some labels may need app restart
  And the selection is saved to app.cfg
```

**Related:** FR-I18N-01, FR-I18N-04, ADR-005

---

### US-SYS-03: Theme Toggle

**As** a User,
**I want** to switch between dark and light themes,
**So that** I can use the app comfortably in any lighting.

**Acceptance Criteria:**

```gherkin
Given the app is in dark theme
When I click the theme toggle button
Then all widgets update to light theme colors
  And all StatusBadges refresh their palette
  And the selection is saved to app.cfg
  And the current session is not affected
```

**Related:** FR-THEME-01, FR-THEME-02, FR-THEME-03