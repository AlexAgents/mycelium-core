# Software Requirements Specification (SRS): Documentation Package

**Version:** 1.0

**Date:** 2026-05-20

**Document Type:** Software Requirements Specification for the Documentation Package

**Associated Project:** MYCELIUM CORE v1.0.0

**Project Base SRS:** docs/reference/srs.md


---

# 1. Purpose and Scope

## 1.1. Purpose

To create a professional, comprehensive, and maintainable documentation
package for the MYCELIUM CORE project, ensuring:

- Rapid onboarding of new developers (target: first build ≤ 30 minutes)
- Architectural understanding of the system (diagrams of all key processes)
- Audit transparency (mapping of SRS requirements to implementation)
- Long-term project support (≥ 5 years)
- Suitability for use as educational material

## 1.2. Target Audience

| Role | What They Should Find |
|---|---|
| **End User** | Installation, first launch, tab-by-tab instructions |
| **Developer / Contributor** | Architecture, API, development guide, tests |
| **Systems Analyst** | UML diagrams, BPMN processes, data models |
| **Security Auditor** | Threat model, SEC checks, audit procedure |
| **Technical Manager** | Decisions (ADR), changelog, metrics |
| **Student / Researcher** | Complete blockchain voting reference |

## 1.3. Documentation Principles

1. **Bilingualism** — all key materials available in both Russian and English
2. **Visualization over text** — every complex process has a diagram
3. **Every diagram has a note** — explaining "why exactly this way"
4. **Single Source of Truth** — each entity is described in exactly one place
5. **Versioning** — documentation has a git history and changelog
6. **Local preview** — static site via MkDocs
7. **"5-second" principle** — any important artifact reachable within 1–2 clicks
8. **Diagram-as-code** — diagrams are stored as text-based source files
9. **Accessibility** — WCAG 2.1 AA compliance where feasible

## 1.4. Quality Metrics

| Metric | Target Value |
|---|---|
| SRS requirements coverage | ≥ 95% (every FR-*, NFR-* mentioned) |
| `src/core/` module coverage in API Reference | 100% |
| `src/ui/` module coverage in user guide | ≥ 80% |
| Time to first project build following docs | ≤ 30 minutes |
| Broken internal links | 0 |
| Linguistic alignment RU↔EN | 100% of keys |

---

# 2. Documentation Technology Stack

## 2.1. Core Stack

| Component | Version | Purpose |
|---|---|---|
| **MkDocs Material** | ≥ 9.5 | Static site generator |
| **mkdocs-static-i18n** | ≥ 1.2 | Multilingual support |
| **mkdocs-mermaid2-plugin** | ≥ 1.1 | Inline Mermaid diagrams |
| **mkdocs-glightbox** | ≥ 0.3 | Lightbox for images |
| **mkdocstrings[python]** | ≥ 0.24 | Auto-generated API from docstrings |
| **PlantUML** | ≥ 1.2024 | UML diagram generation |
| **Camunda Modeler** or **bpmn.io** | latest | BPMN diagram authoring |
| **Figma** (optional) | web | UI mockups |
| **Java Runtime** | ≥ 11 | Required for PlantUML.jar |

## 2.2. Dependency File `docs/requirements-docs.txt`

```
mkdocs>=1.6.0
mkdocs-material>=9.5.0
mkdocs-static-i18n>=1.2.0
mkdocs-mermaid2-plugin>=1.1.0
mkdocs-glightbox>=0.3.0
mkdocstrings[python]>=0.24.0
pymdown-extensions>=10.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
```

## 2.3. Supported Diagram Formats

| Type | Source Format | Export Format | Tool |
|---|---|---|---|
| Component (UML) | `.puml` | `.svg` | PlantUML |
| Class (UML) | `.puml` | `.svg` | PlantUML |
| Sequence (UML) | `.puml` | `.svg` | PlantUML |
| State (UML) | `.puml` | `.svg` | PlantUML |
| Activity (UML) | `.puml` | `.svg` | PlantUML |
| Use Case (UML) | `.puml` | `.svg` | PlantUML |
| Deployment (UML) | `.puml` | `.svg` | PlantUML |
| C4 Architecture | `.puml` + C4 macros | `.svg` | PlantUML |
| Inline (simple) | Mermaid in .md | automatic render | mkdocs-mermaid2-plugin |
| BPMN Business Process | `.bpmn` (XML) | `.svg` | bpmn.io / Camunda |
| UI Mockups | Figma project | `.png` | Figma |
| Screenshots | — | `.png` | OS screenshot tool |

---

# 3. Documentation File Structure

## 3.1. Target `docs/` Structure

```
docs/
├── mkdocs.yml                  # MkDocs config
├── requirements-docs.txt       # Python dependencies
├── scripts/                    # PlantUML script
├── plantuml.jar                # PlantUML binary
│
└── src/                        # MkDocs source
    ├── index.md                # Home page
    ├── getting-started/        # Setup & Run
    ├── user-guide/             # UI Tabs
    ├── architecture/           # Arch & ADRs
    ├── api/                    # Code API
    ├── ui-design/              # UI Design
    ├── deployment/             # Build & Deploy
    ├── security/               # Threat model & Audits
    ├── development/            # Dev guides
    ├── reference/              # SRS, Changelog, FAQ
    │
    └── diagrams/               # Diagram catalog
        ├── index.md
        ├── architecture/       # SVG renders
        ├── sequence/
        ├── state/
        ├── activity/
        ├── usecase/
        ├── bpmn/
        │
        └── sources/            # Diagram sources
            ├── uml/            # .puml (PlantUML)
            └── bpmn/           # .bpmn (Camunda/BPMN.io)
```

## 3.2. Diagram Storage Principle

| File | Under git | Source | Purpose |
|---|---|---|---|
| `*.puml` | Yes | Human-written | UML diagram source |
| `*.bpmn` | Yes | bpmn.io / Camunda | BPMN source |
| `*.svg` (auto) | Yes | `generate_diagrams.py` | Render for display |
| `*.png` (auto) | Yes | `generate_diagrams.py` | Fallback for GitHub preview |
| `*.fig` (Figma) | No | Figma cloud | Stored in Figma project |
| `*.png` (Figma export) | Yes | Manual export | Used in Markdown |

---

# 4. Documentation Section Contents

## 4.1. Home Page (`index.md`)

**Purpose:** Primary entry point to the documentation.

**Contents:**

- Brief project description (1–2 paragraphs)
- Screenshot of the main window
- Badges: version, license, test status, languages
- 4 large link buttons:
  - "Get Started" → `getting-started/installation`
  - "Architecture" → `architecture/overview`
  - "API Documentation" → `api/`
  - "Security" → `security/threat-model`
- Language switcher (provided by MkDocs Material)
- Search (provided by MkDocs Material)

## 4.2. Getting Started

### 4.2.1. `installation.md`

- System requirements (OS, Python ≥ 3.11, RAM, disk)
- Installing Python and pip
- Installing dependencies
- Placing the Geth binary
- Configuring the `.env` file
- Verifying the installation
- Troubleshooting the most common errors

### 4.2.2. `first-run.md`

- Launching the application
- What happens on startup (with screenshots)
- Creating your first vote in 5 minutes
- Each step accompanied by a screenshot

### 4.2.3. `quick-tour.md`

- 5-minute overview of all 4 tabs
- Annotated screenshots with numbered callouts
- Key features of each tab

## 4.3. User Guide

### 4.3.1. `overview.md`

- The concept of "one session = one vote"
- Voting lifecycle
- User roles

### 4.3.2. `admin-tab.md`
Full description of the Admin tab:

- Contract section: deploy, balances, fund from dev
- Candidates section: adding, registration
- Voters section: generation, import, export, whitelist, fund
- Stage section: start/finish voting
- All dialogs (Confirm, Error, Toast)
- Tab screenshot with numbered elements

### 4.3.3. `vote-tab.md`

- Voter authentication
- Status check (whitelisted, has voted, balance)
- Candidate selection
- Mass Vote mode
- QR receipt

### 4.3.4. `audit-tab.md`

- 4 audit modes (Full / Pre / Live / Final)
- Availability depending on stage
- Reading results
- Copy Report / Export JSON / Export CSV
- Understanding SEC checks

### 4.3.5. `logs-tab.md`

- Viewing session logs
- Search, auto-scroll, file information
- Saving, copying

## 4.4. Architecture

### 4.4.1. `overview.md`

- Layered model (diagram)
- Rationale for the chosen architecture
- Links to ADRs
- **Must contain a Component Diagram (PlantUML inline or linked)**

### 4.4.2. `layers.md`

- Detailed description of each layer:
  - **UI Layer:** rules, constraints, responsibilities
  - **Application Layer (Controller):** facade pattern
  - **Domain / Service Layer:** business logic encapsulation
  - **Infrastructure Layer:** Web3, Geth, Solidity
- Inter-layer interaction rules
- List of permitted and prohibited patterns

### 4.4.3. `components.md`

- Description of each component from the Component Diagram
- Purpose, responsibilities, dependencies
- Links to API Reference

### 4.4.4. `data-flow.md`

- Data flow for typical operations:
  - Voting from UI to blockchain
  - Launching an audit
  - Creating a new session
- **Sequence diagrams for each**

### 4.4.5. `decisions/` — ADR (Architecture Decision Records)

Each ADR follows the standard template:

# ADR-XXX: Decision Title

## Status
Accepted | Superseded | Deprecated

## Date
YYYY-MM-DD

## Context
The state of affairs prior to the decision and the problem that arose.

## Decision
What was chosen.

## Alternatives

1. Alternative A — reason for rejection
2. Alternative B — reason for rejection

## Consequences

### Positive

- ...

### Negative

- ...

### Risks

- ...

## Related ADRs

- ADR-XXX (related)

**Mandatory ADRs (minimum 7):**

- ADR-001: PyQt6 vs PySide6
- ADR-002: Geth dev mode vs persistent chain
- ADR-003: Ephemeral chain between runs
- ADR-004: The "one session = one vote" principle
- ADR-005: i18n with runtime switching
- ADR-006: Layered architecture vs MVC/Clean
- ADR-007: ErrorParser separated from AppController

## 4.5. Diagrams

### 4.5.1. `index.md`
Catalog of all diagrams with thumbnails and descriptions.
Grouped by type.

### 4.5.2. Structure of each diagram `.md` file

# Diagram Name

## Brief Description
One or two sentences on purpose.

## Context
The process within which this diagram is used.

## Diagram

`![Diagram name] (../assets/diagrams/category/name.svg)`

## Note / Explanation
**Why exactly this way:**

- Explanation of key decisions
- Explanation of the chosen notation

## Related Artifacts

- ADR: `[ADR-XXX] (../decisions/adr-xxx.md)`
- Code: `src/core/module.py`
- SRS: FR-XXX

## Source
`diagrams/sources/uml/category/name.puml`

## Change History
| Date | Version | Change |
|---|---|---|
| 2026-05-17 | 1.0 | Created |

### 4.5.3. Mandatory Diagrams

**Architecture (UML Component, Class, Deployment, C4):**

| # | Name | Type | Purpose |
|---|---|---|---|
| 1 | component | UML Component | All system components and relationships |
| 2 | class | UML Class | Domain models (Election, Candidate, etc.) |
| 3 | deployment | UML Deployment | Physical placement (Python, Geth, Files) |
| 4 | c4-context | C4 Level 1 | System context |

**Sequence (UML Sequence):**

| # | Name | Purpose |
|---|---|---|
| 5 | deploy-contract | Full contract deployment flow |
| 6 | cast-vote | From clicking "Cast Vote" to confirmation |
| 7 | mass-vote | Mass voting with pre-filtering |
| 8 | new-session | Creating a new session (quick mode) |
| 9 | reset-blockchain | Clean mode (9 steps) |
| 10 | geth-crash-recovery | Behavior upon Geth crash |

**State (UML State Machine):**

| # | Name | Purpose |
|---|---|---|
| 11 | voting-lifecycle | SETUP → ACTIVE → FINISHED |
| 12 | session-states | NotStarted → InProgress → Archived |
| 13 | geth-states | Stopped → Starting → Running → Crashed |

**Activity (UML Activity):**

| # | Name | Purpose |
|---|---|---|
| 14 | precheck-vote | 5 levels of validation before voting |
| 15 | geth-startup | Grace period + port check + retry |
| 16 | audit-process | Audit preparation and execution |

**Use Case (UML Use Case):**

| # | Name | Purpose |
|---|---|---|
| 17 | system-use-cases | All use cases for 3 actors |

**BPMN 2.0 (Business Processes):**

| # | Name | Purpose |
|---|---|---|
| 18 | voting-business-process | Full business process from preparation to results |
| 19 | audit-workflow | Auditor workflow |
| 20 | session-lifecycle | Business lifecycle of a voting session |

**Total minimum: 20 diagrams**

## 4.6. API Reference

Structure for each module:

# Module: AppController

## Purpose
High-level facade between the UI and services.

## Location
`src/core/app_controller.py`

## Dependencies

- `VotingService`
- `AuditService`
- `CompilerService`
- ...

## Public Methods

### `precheck_vote(voter_private_key: str) -> PrecheckResult`
**Purpose:** Full pre-vote validation.

**Parameters:**

- `voter_private_key` (str) — voter's private key

**Returns:**

- `PrecheckResult` — structured result

**Exceptions:**

- `RuntimeError` — if no active session exists

**Example:**

```python
result = controller.precheck_vote("0xabc...")
if result.is_ok:
    controller.cast_vote(...)
```

**Related:**

- `cast_vote()`, `precheck.py`

**Alternative:** auto-generation via `mkdocstrings` from code docstrings.

At minimum, document **all public methods** from:

- `AppController`
- `VotingService`
- `AuditService`
- `ErrorParser`
- `PrecheckResult / PrecheckStatus`
- `GethManager`
- `NonceManager`
- `Web3Provider`
- `CompilerService`

## 4.7. UI Design System

### 4.7.1. `design-system.md`

- Design principles
- Atomic Design structure

### 4.7.2. `color-palette.md`

- Complete palette for both themes
- Semantic meaning of each color
- Accessibility (WCAG 2.1 contrast)
- Hex / RGB values

### 4.7.3. `typography.md`

- Fonts in use
- Size hierarchy
- Weights

### 4.7.4. `components.md`

- Catalog of all UI components
- States (default / hover / disabled / focus)
- Usage examples
- Screenshots

### 4.7.5. `icons.md`

- All qtawesome icons used in the project
- Semantic meaning of each
- Full list for audit purposes

### 4.7.6. `figma-mockups.md`

- Links to the Figma project
- Exported previews of key screens
- Guide to updating mockups

## 4.8. Deployment

### 4.8.1. `from-source.md`

- Developer installation from scratch

### 4.8.2. `pyinstaller.md`

- Building a standalone .exe
- Including resources (icons, themes, i18n)
- Binary signing (optional)
- Creating an installer (optional)

### 4.8.3. `distribution.md`

- Where to publish releases (GitHub Releases)
- Release structure
- Checksum verification

### 4.8.4. `troubleshooting.md`
Comprehensive overview of known issues and solutions from discussions:

- Port 8545 in use
- Geth not mining blocks
- Chain data files locked
- Tests not running (sys.path)
- And so on

## 4.9. Security

### 4.9.1. `threat-model.md`

- STRIDE analysis
- Attack vectors
- Mitigations
- Out-of-scope threats

### 4.9.2. `sec-checks.md`

- Detailed description of SEC-01..06
- How they are implemented in code
- How they are verified automatically

### 4.9.3. `audit-procedure.md`

- Step-by-step procedure for auditing a new release
- Auditor checklist
- Report template

### 4.9.4. `known-limitations.md`

- Ephemeral chain
- Single point of failure (Geth node)
- Impossibility of anonymous voting
- Private key dependency

## 4.10. Development

### 4.10.1. `setup.md`

- IDE setup (VSCode / PyCharm)
- Recommended extensions
- Formatter configuration

### 4.10.2. `testing.md`

- Running pytest
- Test structure
- Coverage
- Adding new tests

### 4.10.3. `style-guide.md`

- PEP 8 + project conventions
- Naming
- Docstring format
- Import order

### 4.10.4. `contributing.md`

- Branch workflow (Git Flow or GitHub Flow)
- Commit message format
- Pull request template
- Code review rules

### 4.10.5. `git-workflow.md`

- Branches (main, develop, feature/*, fix/*)
- Releases (tags, releases)
- Hotfix process

## 4.11. Reference

### 4.11.1. `srs.md`
Copy of the original project SRS (unchanged, for audit purposes).

### 4.11.2. `changelog.md`
Full CHANGELOG in Keep a Changelog format.

### 4.11.3. `glossary.md`
Terminology glossary:

- Whitelist, Stage, Nonce, Genesis, ABI, Bytecode
- Smart Contract, Gas, Wei, ETH
- Pre-check, Audit, Session
- All abbreviations (RPC, SRS, ADR, etc.)

### 4.11.4. `faq.md`
Extended version of the README FAQ plus developer-specific questions.

### 4.11.5. `license.md`
Full text of the MIT license.

---

# 5. Diagram Requirements

## 5.1. Mandatory Elements of Each Diagram

Every diagram must contain:

| Element | Description |
|---|---|
| **Title** | In both languages (EN primary, RU secondary) |
| **Version** | Linked to the project version |
| **Creation date** | YYYY-MM-DD |
| **Last updated date** | YYYY-MM-DD |
| **Author** | Full name or organization |
| **Legend** | Notation key (if non-standard) |
| **Note / Description** | Explanation of "why exactly this way" |
| **References** | Links to ADR, sequence, code |

## 5.2. Style Requirements

### 5.2.1. Color Semantics

| Color | Hex | Meaning |
|---|---|---|
| Blue | #388bfd | UI / Presentation layer |
| Green | #3fb950 | Domain / Service layer |
| Yellow | #e3b341 | Infrastructure |
| Gray | #8b949e | External system |
| Red | #f85149 | Critical / Security boundary |
| Purple | #a78bfa | Data / Storage |

### 5.2.2. Fonts in Diagrams

- Sans-serif for all text
- Monospaced (Consolas) for method names and code
- Minimum 11pt for body text
- Minimum 9pt for labels

### 5.2.3. Arrows and Relationships

- UML standard for relationship types
- Solid arrow — synchronous call
- Dashed arrow — asynchronous / return
- Hollow triangle — inheritance
- Diamond — composition / aggregation

## 5.3. PlantUML — Shared Theme

The unified theme is defined in `src/diagrams/sources/uml/_common/theme.iuml`:

```plantuml
@startuml
!define PRIMARY_COLOR #0969da
!define SUCCESS_COLOR #3fb950
!define WARNING_COLOR #e3b341
!define ERROR_COLOR #f85149
!define UI_COLOR #388bfd
!define DOMAIN_COLOR #3fb950
!define INFRA_COLOR #e3b341

skinparam backgroundColor white
skinparam defaultFontName Arial
skinparam defaultFontSize 12
skinparam shadowing false

skinparam component {
    BackgroundColor white
    BorderColor #444
    ArrowColor #555
}

skinparam class {
    BackgroundColor #f4f7fb
    BorderColor #c4d3e8
    ArrowColor #0969da
}

skinparam sequence {
    ArrowColor #0969da
    LifeLineBorderColor #c4d3e8
    LifeLineBackgroundColor #f4f7fb
    ParticipantBorderColor #444
}
@enduml
```

All .puml files must include:
```plantuml
!include _common/theme.iuml
```

## 5.4. Diagram Generation Script

File `docs/generate_diagrams.py`:

**Functional Requirements:**

- Recursively locates all `.puml` files in `src/diagrams/sources/uml/`
- For each file, invokes the PlantUML jar to generate SVG and PNG
- Places output in `docs/assets/diagrams/<category>/`
- Preserves folder structure
- Logs generation errors
- Supports a `--force` flag for full regeneration
- Supports a `--watch` flag for re-generation on file changes

---

# 6. Documentation Localization Requirements

## 6.1. Language Set

- **English** — primary language, default
- **Russian** — secondary, full coverage

## 6.2. Translation Standards

| English Term | Russian Equivalent |
|---|---|
| Voting | Голосование |
| Candidate | Кандидат |
| Voter | Избиратель |
| Whitelist | Whitelist (untranslated) |
| Smart contract | Смарт-контракт |
| Stage | Стадия |
| Session | Сессия |
| Audit | Аудит |
| Deploy | Деплой / Развёртывание |
| Nonce | Nonce (untranslated) |
| Gas | Газ |

## 6.3. Translation Rules

1. Technical terms (whitelist, nonce, RPC) are **not translated**
2. Translation standards for all key terms are stored in `docs/glossary.md`
3. Every page has a 1:1 correspondence EN↔RU
4. When a page is updated, both versions are updated
5. File names are in English; localization is applied via the `.ru.md` suffix

## 6.4. Localization Coverage

| Content Type | Coverage |
|---|---|
| Home, Getting Started | 100% |
| User Guide | 100% |
| Architecture, Diagram notes | 100% |
| ADR | 100% |
| API Reference | 50% (English primary) |
| UI Design | 100% |
| Deployment, Security | 100% |
| Development | 50% (English primary) |
| Reference | 100% |

---

# 7. Implementation Phases

## 7.1. Phase 1 — Base Infrastructure (1–2 days)

**Deliverable:** A working MkDocs site with minimal content.

**Tasks:**

- Create the `docs/` folder structure
- Configure `mkdocs.yml` (Material theme, i18n, plugins)
- Create `requirements-docs.txt`
- Write `generate_diagrams.py`
- Install PlantUML.jar
- Create `index.md` and `index.ru.md` (stubs)
- Test run of `mkdocs serve`

**Acceptance Criteria:**

- `mkdocs serve` starts without errors
- http://127.0.0.1:8000 opens successfully
- Theme switching works
- Language switching works (even on empty pages)

## 7.2. Phase 2 — Migration of Existing Content (1 day)

**Deliverable:** SRS, Changelog, and Glossary are available in the documentation.

**Tasks:**

- Move `srs.md` → `docs/docs/reference/srs.md`
- Move `changelog.md` → `docs/docs/reference/changelog.md`
- Create `glossary.md`
- Create `faq.md` based on the README FAQ
- Create `license.md`

**Acceptance Criteria:**

- All 5 files appear in navigation
- Markdown formatting is correct
- Links work

## 7.3. Phase 3 — Architectural Diagrams (3–4 days)

**Deliverable:** 4 basic UML diagrams in PlantUML format.

**Tasks:**

- Create the shared theme `_common/theme.iuml`
- Component Diagram (.puml + description in .md)
- Class Diagram (.puml + description in .md)
- Deployment Diagram (.puml + description in .md)
- C4 Context Diagram (.puml + description in .md)
- Run `generate_diagrams.py` and verify SVG output

**Acceptance Criteria:**

- 4 SVG files in `docs/assets/diagrams/architecture/`
- 4 description pages in `docs/docs/diagrams/architecture/`
- Each page has a note with an explanation
- Diagrams use a unified color scheme

## 7.4. Phase 4 — Sequence and State Diagrams (3–4 days)

**Deliverable:** All key processes are visualized.

**Tasks:**

- 6 Sequence diagrams
- 3 State diagrams
- Descriptions for each
- Links to corresponding code and ADRs

**Acceptance Criteria:**

- 9 SVG files
- 9 description pages
- Linkage to FR-* identifiers from the SRS is shown

## 7.5. Phase 5 — Activity and Use Case Diagrams (1–2 days)

**Deliverable:** Activities and use cases described.

**Tasks:**

- 3 Activity diagrams
- 1 Use Case diagram (all actors)
- Descriptions

**Acceptance Criteria:**

- 4 SVG files + descriptions

## 7.6. Phase 6 — BPMN Diagrams (2 days)

**Deliverable:** Business processes described in BPMN 2.0.

**Tasks:**

- Create 3 BPMN files in Camunda Modeler or bpmn.io
- Voting Business Process (with pools: Administrator / Voter / Auditor / System)
- Audit Workflow
- Session Lifecycle
- Export to SVG (manual)
- Descriptions in Markdown

**Acceptance Criteria:**

- 3 .bpmn files committed to git
- 3 SVGs in assets
- 3 description pages

## 7.7. Phase 7 — Architecture Pages (2 days)

**Deliverable:** Full architecture description.

**Tasks:**

- `overview.md` — with inline diagrams
- `layers.md` — detailed layer descriptions
- `components.md` — component catalog
- `data-flow.md` — data flows
- 7 ADRs (based on decisions from our discussions)

**Acceptance Criteria:**

- 4 pages + 7 ADRs
- Each page references at least 1 diagram
- Each ADR follows the template

## 7.8. Phase 8 — User Guide (2–3 days)

**Deliverable:** User instructions with screenshots.

**Tasks:**

- Take 10+ screenshots of all tabs in both themes
- `overview.md` — application concept
- 4 tab-specific files with annotated screenshots
- Usage scenarios

**Acceptance Criteria:**

- 5 User Guide pages
- Minimum 10 screenshots
- Steps are numbered and linked to screenshots

## 7.9. Phase 9 — API Reference (1–2 days)

**Deliverable:** Public API documentation.

**Tasks:**

- Configure mkdocstrings
- Document 9 key modules
- Add usage examples

**Acceptance Criteria:**

- 9 API pages
- All public methods of AppController are covered

## 7.10. Phase 10 — Security & Deployment (2 days)

**Deliverable:** Security and build documentation.

**Tasks:**

- threat-model.md (STRIDE)
- sec-checks.md (details on SEC-01..06)
- audit-procedure.md
- known-limitations.md
- from-source.md
- pyinstaller.md
- distribution.md
- troubleshooting.md (expanded based on discussions)

**Acceptance Criteria:**

- 8 pages
- troubleshooting contains ≥ 15 resolved issues

## 7.11. Phase 11 — UI Design System (2 days)

**Deliverable:** Design system documentation.

**Tasks:**

- design-system.md
- color-palette.md with color swatches
- typography.md
- components.md with previews
- icons.md — full list of qtawesome icons
- figma-mockups.md (if Figma is available)

**Acceptance Criteria:**

- 6 pages
- All icons in use are documented

## 7.12. Phase 12 — Development Guide (1–2 days)

**Deliverable:** Contributor guide.

**Tasks:**

- setup.md
- testing.md
- style-guide.md
- contributing.md
- git-workflow.md

**Acceptance Criteria:**

- 5 pages
- contributing.md contains a PR template

## 7.13. Phase 13 — Full Russian Localization (4–5 days)

**Deliverable:** Fully bilingual documentation.

**Tasks:**

- Translate all 70+ pages into Russian
- Update glossary
- Verify link correctness
- Verify rendering in both languages

**Acceptance Criteria:**

- 100% EN↔RU correspondence
- All internal links work
- Language switcher works on every page

## 7.14. Phase 14 — Final Review and Publication (1–2 days)

**Deliverable:** Production-ready documentation site.

**Tasks:**

- Run Markdown linter
- Check all links (markdown-link-check)
- Verify rendering in browsers (Chrome, Firefox, Safari)
- Test on mobile
- Optional: configure GitHub Actions for auto-deploy
- Optional: deploy to GitHub Pages

**Acceptance Criteria:**

- 0 broken links
- Site opens in all browsers
- Load time ≤ 2 seconds at average connection speed

---

# 8. Summary Acceptance Criteria

The documentation package is considered complete when **all** of the following conditions are met:

## 8.1. Infrastructure

1. `mkdocs serve` starts without errors or warnings
2. The site is accessible at `http://127.0.0.1:8000`
3. Search works in both languages
4. Dark/light themes switch correctly
5. EN/RU languages switch correctly
6. All MkDocs plugins function correctly

## 8.2. Content

7. Minimum 70 pages of content (excluding translations)
8. All 20 mandatory diagrams are created
9. Minimum 7 ADRs in Markdown format
10. SRS, Changelog, Glossary, and FAQ are present
11. API Reference covers 100% of public methods in core modules

## 8.3. Diagrams

12. All PlantUML files render to SVG without errors
13. BPMN files open correctly in bpmn.io
14. Every diagram has an explanatory note
15. Diagram color scheme is consistent throughout
16. A unified PlantUML theme is used

## 8.4. Localization

17. 100% of pages have a Russian version (except API Reference)
18. Glossary contains ≥ 30 terms with translations
19. Language switcher works on all pages
20. Cross-language links are consistent

## 8.5. Quality

21. 0 broken internal links (verified with markdown-link-check)
22. All screenshots reflect the current version (not from beta releases)
23. Markdown files comply with the project style (if a linter is configured)
24. All code examples are correct and executable
25. Last-updated date is shown on every page

## 8.6. Alignment with Project SRS

26. All FR-* identifiers from the SRS are mentioned in at least one location
27. All NFR-* blocks have corresponding sections in the docs
28. All 23 SRS acceptance criteria are reflected in the documentation

---

# 9. Constraints and Assumptions

## 9.1. Constraints

- Documentation does not replace code comments — these are distinct levels
- Not every implementation detail is described (only architecturally significant ones)

## 9.2. Assumptions

- The user has a basic knowledge of Markdown
- Viewing the documentation requires Python and MkDocs (or a browser for the static site)
- BPMN diagrams are created manually via GUI tools
- Figma mockups are optional and may be added at a later stage

---

# 10. Contact Information

**Documentation Owner:** Alex
**Project Owner:** Alex
**Documentation SRS Creation Date:** 2024-05-17

---

## Implementation Status

The documentation package described in this specification has been
fully implemented as part of **MYCELIUM CORE v1.0.1**.

### Delivered Artifacts

1. **MkDocs setup** — `mkdocs.yml`, `requirements-docs.txt`,
   `scripts/build_docs.py`, `scripts/generate_diagrams.py`.
2. **PlantUML diagrams** — 17 diagrams across 5 categories
   (Architecture, Sequence, State, Activity, Use Case).
3. **BPMN 2.0 processes** — 6 business process models with Camunda
   Modeler XML sources.
4. **ADR records** — 7 Architecture Decision Records (ADR-001–007).
5. **API Reference** — 10 core modules documented in EN and RU.
6. **Glossary, FAQ, SRS, Changelog** — all reference pages completed.
7. **Full Russian localization** — 100% EN↔RU parity across all
   sections.

### Location

```text
docs/src/reference/srs-docs.md  ← This specification
```