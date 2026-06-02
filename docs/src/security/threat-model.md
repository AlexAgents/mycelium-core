# Threat Model (STRIDE)

## Analyst Note: Zero-Trust Local Execution
This document analyzes security threats to **MYCELIUM CORE** using the STRIDE methodology. Because this is a standalone desktop application, the threat surface differs significantly from standard web applications. There is no external network exposure, no public mempool, and no multi-user concurrent access. Therefore, the threat model assumes a **Zero-Trust Local Environment** where the primary attack vectors involve local file manipulation and credential theft.

---

## System Context
```text
+-------------------------------+
| Developer's Machine           |
|                               |
|  +----------+      JSON-RPC   |
|  | MYCELIUM |<--------------> |
|  | CORE     |     (loopback)  |
|  +----------+      +------+   |
|       |            | Geth |   |
|       v            +------+   |
|  +-----------+                |
|  | Filesystem|                |
|  | (logs,    |                |
|  | chain,    |                |
|  | keys)     |                |
|  +-----------+                |
+-------------------------------+
```

---

## STRIDE Analysis

### S — Spoofing 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Attacker obtains a voter's private key | Voter's vote is cast by someone else | SEC-06 warning shown on first key input; keys are not persisted by default; `_SecretFilter` redacts keys from logs | **Accepted** — inherent limitation of key-based authentication without hardware wallets |
| Attacker obtains admin private key | Full control over contract (register candidates, change stages) | Admin key not saved by default; dev mode explicitly marked; key field read-only after deploy | Medium — dev mode convenience vs security trade-off |

### T — Tampering 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Modification of `VotingCore.sol` before compilation | Altered contract logic | ABI hash validation via `validate_abi_hash()` in `Web3Provider`; contract source under version control | Low |
| Tampering with `session.log` | False audit trail | Logs are append-only during session; archived on new session; `_SecretFilter` prevents key leakage | Low — no cryptographic log signing |
| Modification of exported JSON results | Falsified audit report | `build_full_report()` reads directly from chain events, not from files | Low |

### R — Repudiation 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Voter denies having voted | Dispute resolution impossible | QR receipt with TX hash + block number provides on-chain proof; `VoteCast` event is immutable | Low |
| Admin denies having changed stage | Accountability gap | `StageChanged` event emitted on-chain; `_check_owner_actions` (SEC-05) verifies all admin TX senders | Low |

### I — Information Disclosure 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Private keys logged to session.log | Key compromise | `_SecretFilter` regex redaction; keyword blocking (`private_key`, `mnemonic`, `secret`) | Low |
| Voters JSON exported with plaintext keys | Key compromise if file shared | `ConfirmDialog` security warning before export; file saved only on explicit user action | Medium — user responsibility |
| Dev admin key in `.env` file | Key compromise if `.env` committed to git | `.env` in `.gitignore`; dev mode badge in UI | Medium |

### D — Denial of Service 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Port 8545 occupied by another process | Application cannot start | `_is_port_in_use()` check + `taskkill` safety net on startup | Low |
| Geth process crash during voting | Votes in flight may fail | `MonitorThread` detects crash; `_crash_signal` notifies UI; `_shutting_down` flag prevents false positives | Low |
| Large chain-data folder consuming disk | Slow startup | `StartupWarnDialog` for >500 MB; `reset_blockchain_data()` with retry | Low |

### E — Elevation of Privilege 
| Threat | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| Non-owner calls admin functions | Unauthorized stage changes or candidate registration | `onlyOwner` modifier on all admin functions in `VotingCore.sol`; SEC-05 audit check | Low — enforced on-chain |
| Non-whitelisted address casts vote | Invalid vote counted | `require(whitelist[msg.sender])` in contract; SEC-02 audit check | Low — enforced on-chain |
| Voter votes twice | Double vote | `require(!hasVoted[msg.sender])` in contract; SEC-01 audit check | Low — enforced on-chain |

---

## Out-of-Scope Threats
The following threats are explicitly **not addressed** by MYCELIUM CORE, as documented in the SRS (Section 3.2):

- **Network-level attacks** (MITM, DNS spoofing) — not applicable, all traffic is loopback.
- **Side-channel attacks** on key derivation — beyond scope of a sandbox.
- **Sybil attacks** — whitelist is admin-controlled, not open registration.
- **Voter coercion / vote buying** — requires cryptographic anonymity (out of scope).
- **Smart contract formal verification** — not performed; contract is intentionally simple.
- **Multi-node consensus attacks** (51%) — single dev-mode node, not applicable.