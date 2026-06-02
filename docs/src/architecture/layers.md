# System Layers

This document provides a detailed description of the responsibilities, constraints, and components of each architectural layer in **MYCELIUM CORE**.

---

## 1. Presentation Layer (UI)

- **Location:** `src/ui/`
- **Key Components:** `MainWindow`, `AdminTab`, `VoteTab`, `AuditTab`, `LogsTab`, and custom widgets (`Toast`, `StatusBadge`).
- **Responsibilities:** Rendering the graphical interface, capturing user input, basic input validation, and dispatching tasks to the application layer.
- **Constraints:**
    - Must **never** import `web3`, `eth_account`, or `solcx`.
    - Must interact with the backend strictly through the `AppController` facade.
    - All long-running operations must be spawned in separate threads using `ThreadRunner` and thin `BaseWorker` subclasses.

## 2. Application Layer (Facade)

- **Location:** `src/core/app_controller.py`
- **Key Components:** `AppController` class.
- **Responsibilities:** Acting as a mediator (Facade) between the UI and domain services, maintaining the session context (`SessionContext`), and coordinating high-level application workflows (such as initialization, new sessions, and safe shutdown).
- **Constraints:**
    - Must not contain low-level blockchain transaction-building logic.
    - Must expose clean, UI-friendly methods, isolating the UI from inner domain models.

## 3. Domain / Service Layer

- **Location:** `src/core/`
- **Key Components:** `VotingService`, `AuditService`, `ErrorParser`, `PrecheckResult`.
- **Responsibilities:** Encapsulating core business rules of the voting process. 
    - `VotingService` handles smart contract interactions, transaction signing, and deployment.
    - `AuditService` parses blockchain events to compile independent statistics and perform cryptographic validations.
    - `ErrorParser` translates raw RPC network errors into human-readable messages.

## 4. Infrastructure Layer

- **Location:** `src/core/` & `src/utils/`
- **Key Components:** `Web3Provider`, `GethManager`, `NonceManager`, `CompilerService`.
- **Responsibilities:** Interfacing with the external environment, operating system, and the Ethereum network. It starts/stops Geth, compiles Solidity code on the fly, provides a unified Web3 connection, and manages thread-safe nonces.