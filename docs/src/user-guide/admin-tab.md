# Admin Tab

The Admin tab is used by the **Administrator** role to prepare and
control an election.

---

## Section 1 — Contract

Controls related to admin authentication and contract deployment.

| Field / Button | Purpose |
|---|---|
| **Admin Private Key** | Private key of the contract owner (the wallet that will deploy and own the contract). Auto-filled in dev mode from `.env`. Read-only after deploy. |
| **Show / Hide eye icon** | Toggles password mask on the key field. |
| **Balance** | Current ETH balance of the admin address. Compact format (4 decimals for normal values, K/M/B/T for large, scientific notation for >1e15). |
| **Dev: X ETH** | Secondary balance label showing the Geth dev account balance (visible only in dev mode). |
| **Fund from Dev** | Transfers 100 ETH from the Geth dev account to the admin address. Available only in dev mode. |
| **Refresh icon** | Reloads admin balance from chain. |
| **Deploy VotingCore** | Compiles `contracts/VotingCore.sol` and deploys to the local chain. One-click operation. |
| **Contract Address** | Address of the deployed contract. Copy-selectable. |
| **Current Stage** | SETUP / ACTIVE / FINISHED (text label). |

After successful deploy:

- Admin key field becomes read-only (locked until New Session).
- Candidate and voter sections unlock.
- Stage display shows `SETUP`.

---

## Section 2 — Candidates

Stage candidates locally, then push to chain in one batch.

| Field / Button | Purpose |
|---|---|
| **Name** | Candidate name. Required. |
| **Party** | Political affiliation. Required. |
| **Ethereum Address** | Candidate's on-chain address. Required. |
| **Generate (magic-wand icon)** | Auto-generates a random valid Ethereum address. |
| **Add** | Appends candidate to the staging table. Validates address format and duplicates. |
| **Candidates table** | Shows staged candidates (Name / Party / Address). Selectable row. |
| **Remove** | Removes selected row from staging. |
| **Register On-Chain** | Sends one `addCandidate` transaction per candidate. Disabled if `< 2` candidates staged. |

Constraints:

- Maximum 10 candidates (enforced by contract).
- Minimum 2 candidates required to start voting.
- After "Register On-Chain": candidate fields lock until New Session.

---

## Section 3 — Voters

Generate, import, fund, and whitelist voters. **Supports drag-and-drop
JSON import** — drop a `voters.json` file anywhere on this group box.

### Row 1: Action buttons

| Button | Purpose |
|---|---|
| **Import** | Open file dialog, load JSON with voters list. |
| **Export** | Save current session voters to JSON. Shows security warning before write (file contains private keys). |
| **Generate** | Generate N test voters (key pairs). Field "Count" controls N (1–1000). |
| **Fund** | Send ETH to all session voters. Field "ETH" controls amount per voter (default 0.01). |

### Row 2: Statistics

- **Loaded** — number of voters in current session memory.
- **Whitelisted** — number successfully added to chain whitelist.
- **Funded** — number successfully funded with ETH.

### Row 3: Whitelist

**Add Voters To Whitelist** — sends one `addVotersBatch` transaction
with all session voter addresses.

### Mini log

Last few lines of the operation log (compile, deploy, fund, whitelist).

---

## Section 4 — Stage Control

Two large buttons:

- **Start Voting** — calls `startVoting()`. Requires:
  - Contract deployed.
  - At least 2 candidates registered.
  - At least 1 voter in whitelist (UX check; contract allows empty).

  Stage transitions to `ACTIVE`. Vote tab becomes usable.

- **Finish Voting** — calls `finishVoting()`. Stage transitions to
  `FINISHED`. Vote tab locks. Audit tab Final/Full modes unlock.

---

## Typical workflow

1. Deploy contract.
2. Add 2+ candidates → Register On-Chain.
3. Generate voters → Fund → Add Voters To Whitelist.
4. Start Voting.
5. Switch to Vote tab.
6. After votes are cast: return here → Finish Voting.
7. Switch to Audit tab.
8. Conduct an audit. Verify the result.
9. Export the voting results and the audit results.
---

## Errors and dialogs

All actionable errors (insufficient funds, nonce conflict, contract
revert) open an **ErrorDialog** with a translated message and an
optional action button (e.g. "Fund this account from admin wallet?").
See `ErrorParser` in the [API Reference](../api/index.md) for the full
list of recognized error patterns.