# MYCELIUM CORE Documentation

Welcome to the technical documentation for **MYCELIUM CORE** — a
desktop sandbox application for modeling, executing, and auditing
blockchain-based voting on a local private Ethereum network.

---

## Project Highlights

This documentation is designed to demonstrate the project architecture:

- **C4 & UML Modeling**: Full system visualization
  (**23 diagrams** across 5 categories).
- **BPMN 2.0 Workflows**: 6 business process models with Camunda
  Modeler XML sources — clear separation of user tasks, UI workers,
  and blockchain execution.
- **Architecture Decision Records (ADR)**: 7 documented decisions
  with transparent rationale for the technology stack, security
  trade-offs, and ephemeral chain design.
- **Event-Driven Audit**: Security invariants verified mathematically
  against independent on-chain event logs (SEC-01..06).

---

## Quick Navigation

### [Getting Started](./getting-started/installation.md)
System requirements, dependency setup, Geth binary, and first-run guide.

### [User Guide](./user-guide/overview.md)
Detailed instructions for each tab: Admin, Vote, Audit, Logs.

### [Architecture](./architecture/overview.md)
Layered architecture design, component maps, and design decisions (ADR).

### [Diagrams](./diagrams/index.md)
Complete set of **23 diagrams** — 17 PlantUML and 6 BPMN 2.0 models:
Component, Class, Sequence, State, Activity, Use Case, and Business
Processes.

### [API Reference](./api/index.md)
Python API reference for all 10 core modules, services, and models.

### [UI Design](./ui-design/design-system.md)
Design system, color palette, typography, component specifications,
icon library, and Figma mockups with 53 annotation notes.

### [Security](./security/threat-model.md)
STRIDE threat model, SEC-01..06 security checks, audit procedure, and
known limitations.

### [Deployment](./deployment/pyinstaller.md)
Building standalone executables, distribution, and troubleshooting.

### [Development](./development/setup.md)
IDE setup, testing guide, code style, contributing, and Git workflow.

### [Reference](./reference/glossary.md)
SRS, User Stories (12 stories with Given/When/Then), Quality Metrics
(23/23 SRS criteria passed), Changelog, Glossary (33 terms),
FAQ (16 questions), License.

---

<div align="center">
<em>Version: 1.0.1 | License: MIT | Author: AlexAgents</em>
</div>