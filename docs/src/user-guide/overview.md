# User Guide Overview

Welcome to the **MYCELIUM CORE** user manual. The application operates as a standalone sandbox environment designed to demonstrate on-chain voting integrity.

---

## Core Concept: One Session, One Vote
Each voting cycle in MYCELIUM CORE is bound to an isolated, single-use smart contract. Re-using contracts is strictly prohibited on the Solidity level. This means:

- Starting a new election session requires deploying a **new contract instance**.
- The smart contract lifecycle strictly moves forward: `Setup -> Active -> Finished`.
- After transition to `Finished`, the state is frozen forever, enabling a reliable cryptographic audit.

## User Roles

1. **Administrator:** Deploys the contract, registers candidates, imports and whitelists voters, and manages state transitions.
2. **Voter:** Authorizes via private key, views candidate listings, and submits a cryptographically signed transaction to cast their vote.
3. **Auditor:** Runs independent checks to verify the security and consistency of the blockchain data.