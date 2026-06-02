<div align="center">

<img src="mycelium-core/src/assets/icons/Original.png"
     alt="MYCELIUM CORE Logo" width="120">

# MYCELIUM CORE

> Desktop sandbox application for modeling, executing, and auditing
> electronic voting on a local Ethereum network.

![Version](https://img.shields.io/badge/version-1.0.1-blue)
[![License](https://img.shields.io/github/license/AlexAgents/mycelium-core?color=yellow)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-41CD52?logo=qt&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-0.8.20-363636?logo=solidity&logoColor=white)
![Tests](https://img.shields.io/badge/tests-180_passed-success)
![Docs](https://img.shields.io/badge/docs-MkDocs_Material-0969da?logo=materialformkdocs&logoColor=white)

[![RU](https://img.shields.io/badge/Language-RU-blue.svg)](README.md)
[![EN](https://img.shields.io/badge/Language-EN-blue.svg)](README.en.md)

**[Artifacts](#artifacts)** ·
**[Architecture](#architecture)** ·
**[Design](#design)** ·
**[Screenshots](#screenshots)** ·
**[Quick Start](#quick-start)** ·
**[Configuration](#Configuration)** ·
**[Security](#security-invariants)** ·
**[FAQ](docs/src/reference/faq.md)** ·
**[Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)**

</div>

---

## Overview

MYCELIUM CORE is a standalone desktop environment designed to simulate
a blockchain-based voting process. The system uses a single Solidity
smart contract (`VotingCore.sol`) as the absolute source of truth, an
ephemeral local Geth node for execution, and a layered PyQt6 graphical
interface.

The project demonstrates the complete lifecycle of on-chain elections,
including preparation, voting, and event-driven cryptographic auditing.

---

## Artifacts

| Category | Artifact | Count | Link |
|:---|:---|:---|:---|
| Documentation | MkDocs Site (EN/RU) | 70+ pages | [Open](docs/src/index.md) |
| UML Diagrams | PlantUML (Component, Class, Sequence, State, Activity, Use Case, Deployment, C4) | 17 | [Catalog](docs/src/diagrams/index.md) |
| BPMN Processes | Camunda Modeler (Setup, Voting, Mass Vote, Audit, Error Handling, Session Lifecycle) | 6 | [Catalog](docs/src/diagrams/index.md) |
| Architecture Decisions | ADR-001 through ADR-007 | 7 | [Overview](docs/src/architecture/overview.md) |
| Security | STRIDE Threat Model + SEC-01..06 | 1+6 | [Threat Model](docs/src/security/threat-model.md) |
| API Reference | Core modules specification | 10 | [API](docs/src/api/index.md) |
| UI Mockups | Figma file with 53 annotation notes | 53 notes | [View in Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) |
| UI Design System | Color palette, typography, components | 6 pages | [Design System](docs/src/ui-design/design-system.md) |
| SRS | Original + Documentation SRS | 2 | [SRS](docs/src/reference/srs.md) |
| Tests | Unit + Integration (real Geth) | 180 passed | [Testing](docs/src/development/testing.md) |
| Glossary | Terms and abbreviations | 33 terms | [Glossary](docs/src/reference/glossary.md) |
| FAQ | Common questions | 16 questions | [FAQ](docs/src/reference/faq.md) |

---

## Architecture

The system enforces a strict layered architecture. The Presentation
Layer (UI) is prohibited from importing Web3, Solidity, or cryptography
libraries directly.

```text
┌─────────────────────────────────────┐
│  UI Layer (PyQt6 Widgets + Workers) │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  AppController (Facade)             │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  Services (Voting / Audit / Error)  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ Infrastructure (Web3 / Geth / Nonce)│
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  VotingCore.sol (Smart Contract)    │
└─────────────────────────────────────┘
```

---

## Design

UI mockups with a complete annotation system are maintained in Figma.

**[View Figma file (read-only)](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)**

The file contains:
- 4 tab mockups (Admin, Vote, Audit, Logs)
- 5 dialog types (New Session, Mass Vote, Funding, Exit, Reset)
- Variative components (StatusBadge, Toast, ProgressBar, LogBox)
- 53 annotation notes with color-coded categories
- Pin markers linking notes to interface elements

Full specification: [Design System](docs/src/ui-design/design-system.md) |
[Color Palette](docs/src/ui-design/color-palette.md) |
[Figma Structure](docs/src/ui-design/figma-mockups.md)

---

## Screenshots

<details>
<summary>🖥️ Admin Tab — contract deployment, candidates, voters, stage control</summary>

<br>

<table>
<tr>
<th align="center">Dark Theme</th>
<th align="center">Light Theme</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/admin-tab-dark.png"
     alt="Admin Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/admin-tab-light.png"
     alt="Admin Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>🗳️ Vote Tab — voter authentication, candidate selection, QR receipt</summary>

<br>

<table>
<tr>
<th align="center">Dark Theme</th>
<th align="center">Light Theme</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/vote-tab-dark.png"
     alt="Vote Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/vote-tab-light.png"
     alt="Vote Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>🔍 Audit Tab — SEC-checks, results, export</summary>

<br>

<table>
<tr>
<th align="center">Dark Theme</th>
<th align="center">Light Theme</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/audit-tab-dark.png"
     alt="Audit Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/audit-tab-light.png"
     alt="Audit Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>📋 Logs Tab — session log, live search, autoscroll</summary>

<br>

<table>
<tr>
<th align="center">Dark Theme</th>
<th align="center">Light Theme</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/logs-tab-dark.png"
     alt="Logs Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/logs-tab-light.png"
     alt="Logs Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>ℹ️ Dialogs — About, Reset Blockchain</summary>

<br>

<table>
<tr>
<th align="center">About Dialog</th>
<th align="center">Reset Blockchain Dialog</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/about-dialog.png"
     alt="About Dialog" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/reset-blockchain-dialog.png"
     alt="Reset Blockchain Dialog" width="480">
</td>
</tr>
</table>

</details>

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [Go-Ethereum (Geth)](https://geth.ethereum.org/downloads/) binary
  placed in the `mycelium-core/bin/` directory
  (`bin/geth.exe` for Windows, `bin/geth` for Linux/macOS).

### 2. Installation

```bash
git clone https://github.com/AlexAgents/mycelium-core.git
cd mycelium-core/mycelium-core
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### 3. Run Application

```bash
python main.py
```

### 4. Run Documentation (MkDocs)

To render UML diagrams locally, download
[`plantuml.jar`](https://github.com/plantuml/plantuml/releases/) and
place it inside the `docs/` directory.

```bash
cd ../../docs
pip install -r requirements-docs.txt
mkdocs serve
# Open http://127.0.0.1:8000
```

---

## Configuration

All runtime parameters are configured via `.env`.
Copy `.env.example` to `.env` and adjust as needed.

### Geth modes

The application runs Geth in `--dev` mode only. This is by design
(see [ADR-002](docs/src/architecture/decisions/adr-002-geth-dev-mode.md)).

| Parameter | Default | Description |
|---|---|---|
| `RPC_HOST` | `127.0.0.1` | Geth JSON-RPC host |
| `RPC_PORT` | `8545` | Geth JSON-RPC port |
| `GETH_NETWORK_ID` | `1337` | Local network ID |

### Transaction parameters

| Parameter | Default | Description |
|---|---|---|
| `DEFAULT_GAS` | `500000` | Gas limit per transaction |
| `DEFAULT_GAS_PRICE` | `1000000000` | Gas price in Wei (1 Gwei) |

### UI timing parameters

These are hardcoded constants — change in source if needed:

| Constant | File | Default | Description |
|---|---|---|---|
| `_TOAST_DURATION_MS` | `src/ui/widgets/toast.py` | `2500` | Toast visible duration (ms) |
| `_TOAST_GAP_MS` | `src/ui/widgets/toast.py` | `150` | Gap between toasts (ms) |
| `--dev.period` | `src/core/geth_manager.py` | `5` | Seconds between Geth blocks |
| `RPC_WAIT_TIMEOUT_SEC` | `src/core/web3_provider.py` | `30` | RPC connection timeout (s) |
| `timeout` | `src/core/voting_service.py` | `120` | TX confirmation timeout (s) |

### Dev mode

| Parameter | Default | Description |
|---|---|---|
| `DEV_MODE` | `true` | Enables dev conveniences |
| `DEV_ADMIN_KEY` | *(empty)* | Auto-fills admin key field on startup |
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG / INFO / WARNING |
| `SOLIDITY_VERSION` | `0.8.20` | Solidity compiler version |

---

## Security Invariants

Critical business rules are enforced proactively on-chain and verified
reactively off-chain via `AuditService`:

| Code | Check | Contract Enforcement | Audit Verification |
|---|---|---|---|
| SEC-01 | Double Vote | `hasVoted[msg.sender]` | No duplicate `VoteCast` events |
| SEC-02 | Whitelist | `require(whitelist[msg.sender])` | All voters are in whitelist |
| SEC-03 | Stage | `onlyStage(Stage.Active)` | Events within `[start, end]` blocks |
| SEC-04 | Candidates | `require(candidates[c].registered)` | Votes target registered addresses |
| SEC-05 | Owner Actions | `onlyOwner` modifier | Admin TXs originate from contract owner |
| SEC-06 | Vote Integrity | implicit `votes += 1` | Event count equals sum of candidate votes |

---

## License

Distributed under the **MIT** License. See [LICENSE](LICENSE) for details.

**Author:** AlexAgents