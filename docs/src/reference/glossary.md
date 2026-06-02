# Glossary
Key terms used in the **MYCELIUM CORE** ecosystem.

---

## Blockchain Terms
| Term | Definition |
|---|---|
| **ABI** | Application Binary Interface — JSON specification describing the smart contract's public methods, events, and data types. Used by Web3 to encode/decode calls. |
| **Bytecode** | Compiled binary representation of a Solidity smart contract, deployed to the blockchain. |
| **Deploy** | The process of publishing a compiled smart contract to the blockchain by sending a creation transaction. |
| **ETH** | Ether — the native cryptocurrency of the Ethereum network. Used to pay for gas. |
| **Gas** | A unit measuring the computational effort required to execute operations on the Ethereum network. |
| **Geth (go-ethereum)** | The official Go implementation of the Ethereum protocol. Used locally in `--dev` mode. |
| **Genesis Block** | The first block (block 0) of a blockchain. In dev mode, created automatically. |
| **JSON-RPC** | A stateless, lightweight remote procedure call protocol using JSON. Geth exposes this on port 8545. |
| **Nonce** | A sequential transaction counter for an account. Prevents replay attacks and guarantees order. |
| **RPC** | Remote Procedure Call — the communication protocol between the application and the Geth node. |
| **Smart Contract** | A self-executing digital contract with terms written in code, deployed on the blockchain. |
| **Transaction Receipt** | A data structure returned by the node after a transaction is mined, containing status, gas used, logs, and block number. |
| **Wei** | The smallest denomination of ETH. 1 ETH = 10^18 Wei. |
| **Whitelist** | A list of Ethereum addresses registered on-chain that are authorized to cast votes. |

## Application Terms
| Term | Definition |
|---|---|
| **ADR** | Architecture Decision Record — a document capturing an important architectural decision, its context, and consequences. |
| **Audit** | The process of verifying election integrity by analyzing on-chain events independently from the contract state. |
| **AppController** | The Facade class coordinating all domain services and exposing clean methods to the UI layer. |
| **BPMN** | Business Process Model and Notation — a standard for modeling business workflows. |
| **Candidate** | A person or entity registered on-chain to receive votes in an election. |
| **Dev Mode** | A convenience mode where the admin private key is auto-loaded from `.env`. Explicitly marked as insecure in the UI. |
| **ErrorParser** | A domain service that translates raw RPC/contract errors into i18n-keyed, human-readable messages. |
| **Facade** | A design pattern providing a simplified interface to a complex subsystem. `AppController` implements this pattern. |
| **Mass Vote** | A testing feature that automatically casts random votes for multiple voters from a JSON file or session. |
| **NonceManager** | A thread-safe utility that tracks and issues sequential nonces for blockchain transactions. |
| **Precheck** | A 5-level validation pipeline executed before sending a vote transaction (key validity, contract deployed, whitelist, has_voted, balance). |
| **QR Receipt** | A QR code image encoding the transaction hash, voter address, candidate address, block number, and session ID. |
| **QSS** | Qt Style Sheet — CSS-like styling language for PyQt6 widgets. |
| **SEC-check** | One of six security invariants (SEC-01 through SEC-06) verified by the AuditService. |
| **Session** | An isolated, single-use voting context bound to one deployed contract instance. |
| **SessionContext** | An in-memory data structure holding the current session's state (contract address, candidates, voters, deploy block). |
| **SRS** | Software Requirements Specification — the formal requirements document for the project. |
| **Stage** | One of three contract lifecycle phases: SETUP → ACTIVE → FINISHED. Transitions are irreversible. |
| **Toast** | A floating notification widget that appears briefly in the bottom-right corner of the window. |
| **Voter** | An Ethereum address registered in the whitelist and authorized to cast exactly one vote. |
| **VoteReceipt** | A typed DTO containing the transaction hash, block number, addresses, and optional QR bytes. |
| **Worker** | A `QThread`-based background task that performs long-running operations without blocking the UI. |
| **VoterStatus** | A typed DTO representing a snapshot of a voter's state (whitelist, voted, balance, stage). Added in v1.0.1 to decouple UI from RPC. |
| **PrecheckResult** | A typed result object returning the status of the 5-level pre-vote validation pipeline. |
| **ParsedError** | A structured representation of a parsed RPC or contract error, containing i18n keys for UI translation. |
| **ResetBlockchainWorker** | A background background worker responsible for safely halting Geth, wiping chain-data, and re-initializing the environment. |

## Abbreviations
| Abbreviation | Expansion |
|---|---|
| ABI | Application Binary Interface |
| ADR | Architecture Decision Record |
| BPMN | Business Process Model and Notation |
| C4 | Context, Containers, Components, Code (architecture model) |
| DTO | Data Transfer Object |
| ETH | Ether |
| GUI | Graphical User Interface |
| i18n | Internationalization |
| MIT | Massachusetts Institute of Technology (license) |
| PoA | Proof of Authority |
| QR | Quick Response (code) |
| QSS | Qt Style Sheet |
| RPC | Remote Procedure Call |
| SEC | Security (check identifier prefix) |
| SRS | Software Requirements Specification |
| SVG | Scalable Vector Graphics |
| TX | Transaction |
| UI | User Interface |
| UML | Unified Modeling Language |
| UUID | Universally Unique Identifier |