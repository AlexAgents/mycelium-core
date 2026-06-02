# Quick Tour

A 2-minute overview of all four tabs in **MYCELIUM CORE**.

---

## Layout

```text
+-- Header --------------------------------------------+
| MYCELIUM CORE    [New Session] [Reset] [Lang] [...]  |
+-- Tabs ----------------------------------------------+
| [ Admin ] [ Vote ] [ Audit ] [ Logs ]                |
+-- Tab content ---------------------------------------+
|                                                      |
|                                                      |
+-- Footer --------------------------------------------+
| Status | Progress | Stage | Connected | Block | ...  |
+------------------------------------------------------+
```

---

## Admin tab

For the **Administrator** role. Used to set up an election.

Sections:

- **Contract** — Admin private key entry, balance, **Fund from Dev**,
  **Deploy VotingCore**, contract address, current stage display.

- **Candidates** — add candidates (Name, Party, Address), generate test
  addresses, register on-chain.

- **Voters** — generate test voters, import / export JSON, fund voters
  with gas, add to whitelist. Drag-and-drop JSON import supported.

- **Stage Control** — start / finish voting.

Buttons are stage-aware: voter actions lock after voting starts,
candidate actions lock after registration.

---

## Vote tab

For the **Voter** role. Used to cast a single vote or run mass voting.

Sections:

- **Voter Authentication** — paste private key or load JSON. Status
  fields (Whitelisted / Has Voted / Stage / Balance) update via async
  worker — no UI freeze on typing.

- **Candidate Selection** — load candidates from chain, choose one.
- **Action** — Cast Vote (single).
- **Receipt** — TX Hash, copy button, QR receipt (140x140 px).
- **Mass Vote (Testing)** — From JSON file or From Session, runs a
  pre-filtered batch with progress log.

---

## Audit tab

For the **Auditor / Researcher** role. Verifies election integrity
on-chain.

Sections:

- **Results** — winner, candidate vote counts, refresh button.
- **Security Checks** — audit mode selector (Full / Pre / Live /
  Final), Run Audit button, table of six SEC-checks with status badges.

- **Export** — Copy Report (JSON to clipboard), Export JSON, Export CSV.

Audit mode availability adapts to the current contract stage. Modes
that don't apply are disabled in the combo.

---

## Logs tab

For all roles. Reads `data/logs/active/session.log` in real time.

Features:

- **Refresh** — reload from disk.
- **Search** — live filter by substring.
- **Autoscroll** — checkbox for tailing the log.
- **Copy All** / **Save As** — clipboard or file export.
- **Clear Display** — clears the viewer (file is **not** deleted).

Bottom info bar: line count, file size, full path.

---

## Header actions

- **New Session** — archive current session, start fresh in the same
  Geth instance (fast mode).

- **Reset Data (TEST)** — deep reset: stop Geth, wipe chain data,
  restart. See ADR-003 for context.

- **Language** combo — switch EN / RU instantly (some labels need
  app restart for full translation).

- **Theme** button — toggle dark / light.
- **About** — version info, license, GitHub link.
- **Exit** — confirm and shut down cleanly.

---

## Footer status indicators

- **Status** — last operation result.
- **Progress** — gradient bar for long operations.
- **Stage** — SETUP / ACTIVE / FINISHED badge.
- **Connected / Offline** — RPC status.
- **Geth** — mode badge (DEV / CUSTOM).
- **Client** — Geth version string.
- **Block** — current block number (updates every 2s).
- **Contract** — deployed address or "not deployed".

---

## Next steps

- Detailed per-tab documentation: see [User Guide](../user-guide/overview.md).
- Architecture: [Overview](../architecture/overview.md).
- Security: [SEC-checks](../security/sec-checks.md).