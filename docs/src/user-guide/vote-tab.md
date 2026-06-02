# Vote Tab

The Vote tab is used by the **Voter** role to authenticate and cast
a vote. It also includes a **Mass Vote** mode for load testing.

---

## Section 1 — Voter Authentication

| Field / Button | Purpose |
|---|---|
| **Private Key** | Voter's private key (hex string, with or without `0x` prefix). Password-masked by default. |
| **Show / Hide eye icon** | Toggles password mask. |
| **Load JSON** | Loads the first voter's key from a `voters.json` file. |

### Status grid

Five status blocks update **automatically** ~600 ms after the last
keystroke (debounced async query):

- **Address** — derived from the private key (truncated for display).
- **Whitelisted** — `YES` (green) / `NO` (red).
- **Has Voted** — `NO` (green) / `YES` (red).
- **Stage** — current contract stage with color coding.
- **Balance** — voter's ETH balance.

> **Note (v1.0.1):** before refactoring, the UI froze for ~50–200 ms on
> every keystroke because of three synchronous RPC calls. Status
> queries now run in a dedicated `VoterStatusWorker` thread.

---

## Section 2 — Candidate Selection

- **Load Candidates** — fetches the registered candidate list from
  the contract. Required after the Admin tab registers them, unless
  auto-load was triggered.

- **Candidate list** — radio buttons. Each row: Name | Party | Address.

Exactly one candidate can be selected.

---

## Section 3 — Action

**CAST VOTE** — sends a `castVote(candidate)` transaction signed with
the entered private key.

Before sending, the application runs a **5-level pre-check**
(`AppController.precheck_vote`):

1. Key valid?
2. Contract deployed?
3. Address in whitelist?
4. Has the address already voted?
5. Balance sufficient for gas (>= 0.0003 ETH)?

If any check fails, the user gets a translated warning dialog and the
transaction is **not** sent (saves gas). See the activity diagram
[Pre-vote Validation](../diagrams/activity/precheck-vote.md).

---

## Section 4 — Receipt

After a successful vote:

- **TX Hash** — transaction hash, copy button next to it.
- **QR receipt** — 140x140 px image encoding TX hash, voter address,
  candidate address, block number, session ID. Save with **Save QR**.

The private key field is cleared automatically.

---

## Section 5 — Mass Vote (Testing)

For load testing and demo: cast random votes for many voters
automatically.

Two source modes:

- **From JSON file** — pick a `voters.json` file.
- **From Session** — use the voters generated in the Admin tab.

Pipeline per voter:

1. Pre-check (key valid, whitelist, has voted, balance).
2. Skip if any check fails — log reason.
3. Random candidate selection.
4. Cast vote.
5. Append to mass-vote log.

After completion, a toast shows: `Voted N, skipped M, failed K`.

Mass Vote does **not** stop on single failure; processing continues
to the next voter.

---

## Stage-aware blocking

The Vote tab blocks operations based on current stage:

| Stage | Behavior |
|---|---|
| **No contract** | "Deploy contract first" dialog blocks any vote. |
| **SETUP** | "Voting has not started" dialog blocks. |
| **ACTIVE** | Voting allowed. |
| **FINISHED** | "Voting has finished" dialog blocks. |

---

## Errors

All transaction errors (insufficient gas, double vote, not whitelisted,
nonce conflict) are translated via `ErrorParser` and shown in
**ErrorDialog**. Localization keys: `err.parser.*` (see project i18n).