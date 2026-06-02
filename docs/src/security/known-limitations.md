# Known Limitations

Documented constraints of the **MYCELIUM CORE** system that are
accepted by design.

---

## 1. Ephemeral Blockchain

Geth `--dev` mode stores state in RAM. All data is lost on restart.
This is intentional — see [ADR-003](../architecture/decisions/adr-003-ephemeral-chain.md).

**Impact:** Deployed contracts and votes do not survive application restarts.
**Mitigation:** "One session = one voting" principle. Export results before closing.

## 2. Single Point of Failure (Geth Node)

The entire system depends on a single local Geth process. If Geth
crashes, all blockchain operations stop.

**Impact:** Votes in flight may fail.
**Mitigation:** `MonitorThread` detects crashes and notifies UI via `_crash_signal`.

## 3. No Voter Anonymity

Votes are linked to Ethereum addresses. Anyone with access to the
chain can see which address voted for which candidate.

**Impact:** No ballot secrecy.
**Mitigation:** Out of scope for this sandbox. Real elections require zero-knowledge proofs or similar cryptographic schemes.

## 4. Key-Based Authentication

Anyone with a voter's private key can vote on their behalf. There is
no multi-factor authentication or biometric verification.

**Impact:** Key theft = vote theft.
**Mitigation:** SEC-06 warning shown once per session. Keys cleared from UI after use. `_SecretFilter` redacts keys from logs.

## 5. No Formal Verification

The `VotingCore.sol` smart contract has not been formally verified.
It relies on unit tests and manual code review.

**Impact:** Undiscovered contract bugs are possible.
**Mitigation:** Simple contract design (< 200 lines). Six automated SEC-checks validate invariants post-hoc.

## 6. Windows File Lock Issues

On Windows, Geth may hold file locks on `chain-data/` after termination.
`reset_blockchain_data()` uses `rmtree_with_retry` with progressive
backoff (up to 8 attempts) to handle this.

**Impact:** Occasional "Reset failed" errors on fast repeated resets.
**Mitigation:** 2-second sleep after Geth stop; `taskkill /F /T` as fallback; UI shows manual cleanup instructions if all retries fail.

## 7. Maximum 10 Candidates

The contract enforces a hard limit of 10 candidates. This is a design
decision for simplicity, not a technical limitation.

## 8. Maximum ~1000 Test Voters

Generating and funding more than ~1000 voters in a single batch may
cause slow performance due to sequential nonce management.

## 9. Real Ethereum Accounts and Private Keys

**Will real ETH be spent if a real account private key is used?**

No. MYCELIUM CORE runs on a local Geth `--dev` node with
`GETH_NETWORK_ID=1337`. This is a completely isolated network —
transactions never reach Ethereum mainnet (chain ID 1) or any public
testnet.

Even if a real Metamask or hardware wallet private key is pasted into
the application:
- The Ethereum address is correctly derived ✅
- The transaction is correctly signed ✅
- The transaction is sent **only** to the local Geth dev node ✅
- Nothing is broadcast to any public network ✅
- **Real ETH is never spent** ✅

**However — key security risk exists:**
Pasting a real private key into a desktop application is dangerous
regardless of network isolation:
- The key exists in process memory while the application runs.
- `_SecretFilter` redacts key patterns from logs, but best-effort only.
- If the machine is compromised, the key could be extracted.

**Recommendation:** Always use generated test keys (Admin tab →
Generate, or `python -c "from src.utils.crypto import
generate_eth_keypair; print(generate_eth_keypair())"`) and never
paste keys that control real funds.

---

## References

- **SRS:** Section 3.2 (Out of Scope)
- **Threat Model:** [threat-model.md](./threat-model.md)