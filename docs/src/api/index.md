# API Reference

Technical specifications for **MYCELIUM CORE** core modules.

---

## Core Services

| Module | File | Description |
|---|---|---|
| **[AppController](./controller.md)** | `app_controller.py` | Primary Facade between UI and domain layers |
| **[VotingService](./voting-service.md)** | `voting_service.py` | Blockchain transaction management |
| **[AuditService](./audit-service.md)** | `audit_service.py` | Event-based security verification |
| **[ErrorParser](./error-parser.md)** | `error_parser.py` | RPC error translation to i18n keys |
| **[Precheck](./precheck.md)** | `precheck.py` | Pre-vote 5-level validation |
| **[GethManager](./geth-manager.md)** | `geth_manager.py` | Geth process lifecycle |
| **[NonceManager](./nonce-manager.md)** | `nonce_manager.py` | Thread-safe nonce tracking |
| **[Web3Provider](./web3-provider.md)** | `web3_provider.py` | Singleton RPC connection |
| **[CompilerService](./compiler-service.md)** | `compiler_service.py` | Solidity compilation |
| **[Models](./models.md)** | `models.py` | Domain DTOs and dataclasses |