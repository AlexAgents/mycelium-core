# System Components

This document outlines the primary software modules of **MYCELIUM CORE** and defines their scope and responsibilities.

---

## Module Directory

### 1. GethManager

- **File:** `src/core/geth_manager.py`
- **Responsibility:** Manages the lifecycle of the local Geth (go-ethereum) process in `--dev` mode. It ensures that port `8545` is free before launching, handles unexpected process termination, and safely kills zombie processes on Windows.

### 2. CompilerService

- **File:** `src/core/compiler_service.py`
- **Responsibility:** Compiles `VotingCore.sol` on the fly using `py-solc-x`. It verifies the compiler installation, saves the generated ABI and bytecode to `contracts/abi/`, and loads compiled artifacts for deployment.

### 3. Web3Provider

- **File:** `src/core/web3_provider.py`
- **Responsibility:** Manages the active JSON-RPC connection to the Ethereum node. It acts as a singleton connector, implements safe wait-for-connection polling, and provides unified low-level network access.

### 4. NonceManager

- **File:** `src/core/nonce_manager.py`
- **Responsibility:** Provides thread-safe, concurrent-safe tracking of account nonces. It prevents transaction collisions when executing rapid batch operations (such as registering 50 voters at once).

### 5. VotingService

- **File:** `src/core/voting_service.py`
- **Responsibility:** Coordinates on-chain voting transactions. It compiles transactions, estimates gas costs, signs transactions with private keys, broadcasts them to the network, and awaits execution receipts.

### 6. AuditService

- **File:** `src/core/audit_service.py`
- **Responsibility:** Performs the security audit of the election. It queries logs for `VoteCast` and `StageChanged` events, aggregates statistics independently from the contract state, and runs validation checks (SEC-01 through SEC-06).