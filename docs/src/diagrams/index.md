# Diagram Catalog

This section contains a complete set of UML and BPMN 2.0 diagrams
documenting the architecture, state machines, and business processes
of **MYCELIUM CORE**.

**Total: 23 diagrams** (17 PlantUML + 6 BPMN 2.0 specifications).

---

## 1. Structural Diagrams

Static structure of the codebase, modules, and physical deployment nodes.

- **[Component Diagram](./architecture/component-diagram.md)** —
  Architectural layers, internal interfaces, and boundaries.
- **[Class Diagram](./architecture/class-diagram.md)** —
  Domain models, DTO structure, and relationships.
- **[Deployment Diagram](./architecture/deployment-diagram.md)** —
  Process topology, filesystem layout, and network loopback.
- **[C4 Context Diagram](./architecture/c4-context.md)** —
  System boundary, external systems, and primary actors.

---

## 2. Sequence Diagrams

Step-by-step transaction scenarios and task execution pipelines.

- **[Deploy Contract](./sequence/deploy-contract.md)** —
  Compilation and smart contract deployment flow.
- **[Cast Vote](./sequence/cast-vote.md)** —
  Single vote transaction: from private key to QR receipt.
- **[Mass Vote](./sequence/mass-vote.md)** —
  Batch testing scenario with pre-check filtering.
- **[New Session](./sequence/new-session.md)** —
  UI reset and log archiving in fast mode.
- **[Reset Blockchain](./sequence/reset-blockchain.md)** —
  Deep clean and Geth re-initialization in clean mode.
- **[Geth Crash Recovery](./sequence/geth-crash-recovery.md)** —
  Process monitoring and UI notification flow on node crash.

---

## 3. State Diagrams

Lifecycle and state transition models.

- **[Voting Contract Lifecycle](./state/voting-lifecycle.md)** —
  Unidirectional smart contract stages: SETUP → ACTIVE → FINISHED.
- **[Session Context States](./state/session-states.md)** —
  In-memory application state transitions.
- **[GethManager States](./state/geth-states.md)** —
  Background blockchain process state machine.

---

## 4. Activity Diagrams

Step-by-step algorithms for logical pipelines.

- **[Pre-vote Validation](./activity/precheck-vote.md)** —
  5-level automatic voter validation pipeline.
- **[Geth Startup Flow](./activity/geth-startup.md)** —
  Port verification and node initialization logic.
- **[Auditor Pipeline](./activity/audit-process.md)** —
  Cryptographic audit execution and result assembly.

---

## 5. Use Case Diagrams

Actor-level interaction models.

- **[System Use Cases](./usecase/system-use-cases.md)** —
  All use cases for 3 actors: Administrator, Voter, Auditor.

---

## 6. Business Processes (BPMN 2.0)

Standard business process models. Each diagram uses 2 pools for clean
readability. XML sources open in Camunda Modeler.

- **[Voting Setup Phase](./bpmn/voting-setup-phase.md)** —
  Administrator preparation: deploy, candidates, voters, whitelist, start.
- **[Voting Cast Phase](./bpmn/voting-cast-phase.md)** —
  Voter authentication, precheck, vote submission, QR receipt.
- **[Mass Vote Pipeline](./bpmn/mass-vote-pipeline.md)** —
  Batch voting with 4-level pre-filtering.
- **[Audit Workflow](./bpmn/audit-workflow.md)** —
  SEC-check execution and report export.
- **[Session Lifecycle](./bpmn/session-lifecycle.md)** —
  Fast/Clean reset and session archiving.
- **[Error Handling](./bpmn/error-handling.md)** —
  Error flow from RPC through ErrorParser to translated UI dialogs.