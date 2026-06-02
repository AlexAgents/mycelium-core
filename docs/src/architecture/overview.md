# Architectural Overview

This document provides a high-level description of the **MYCELIUM CORE** system architecture. The system is built using a strict layered architecture pattern to ensure maintainability, testability, and a clean separation of concerns.

---

## High-Level Block Diagram

The interaction flow between system components follows a unidirectional
dependency model from the Presentation layer down to the Smart Contract.
For a detailed component-level view see the
[Component Diagram](../diagrams/architecture/component-diagram.md).

```text
┌─────────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER (UI)            │
│                 src/ui/ (PyQt6 Widgets)            │
└──────────────────────────────┬──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                APPLICATION LAYER (Facade)          │
│               src/core/app_controller.py           │
└──────────────────────────────┬──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 DOMAIN / SERVICE LAYER             │
│             src/core/ (Voting/Audit Services)      │
└──────────────────────────────┬──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER              │
│        src/core/ (Web3Provider / GethManager)      │
└──────────────────────────────┬──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                     SMART CONTRACT                 │
│                 contracts/VotingCore.sol           │
└─────────────────────────────────────────────────────────┘
```

## Architectural Principles

1. **Unidirectional Dependency:** Upper layers can reference lower layers,
   but lower layers must never import components from upper layers.
2. **UI-Web3 Isolation:** The Presentation layer is completely decoupled
   from Web3 and Ethereum-specific classes. It interacts solely with the
   `AppController` facade.
3. **Single Source of Truth:** The smart contract deployed on the local
   private blockchain serves as the absolute source of truth for all
   election states, candidates, whitelists, and votes.
4. **Thread Isolation:** Long-running blockchain transactions and node
   management operations are delegated to async workers running in
   separate threads, preventing UI lockups.

---

## Further Reading

| Topic | Document |
|---|---|
| Layer responsibilities | [System Layers](./layers.md) |
| Component catalog | [Components](./components.md) |
| Component Diagram (UML) | [Component Diagram](../diagrams/architecture/component-diagram.md) |
| Data flow details | [Data Flow](./data-flow.md) |
| Key decisions | [ADR-006 Layered Architecture](./decisions/adr-006-layered-architecture.md) |