# First Run

This guide walks through your first complete voting cycle in
**MYCELIUM CORE** — from deployment to audit. Estimated time: 5 minutes.

---

## What happens on startup

When you launch `python main.py`:

1. **Geth boots up** (~2 seconds). The footer badge shows `OFFLINE → CONNECTED`.
2. **A new session is created.** UUID is generated, log file opens.
3. **The main window opens** on the Admin tab in `SETUP` stage.

If you see a red `GETH CRASHED` badge, see [Troubleshooting](installation.md#troubleshooting).

---

## Complete a voting cycle

### 1. Admin tab — deploy the contract

1. The **Admin Private Key** field is auto-filled in dev mode.
2. Click **Fund from Dev** to transfer 100 ETH from the dev account to
   your admin address.

3. Click **Deploy VotingCore**.

Wait for the toast `Contract deployed`. The contract address appears
in the footer.

### 2. Add candidates

1. Fill **Name**, **Party**, **Ethereum Address**. Use **Generate** to
   auto-create a test address.

2. Click **Add** to stage the candidate.
3. Repeat for at least 2 candidates (the contract requires `>= 2`).
4. Click **Register On-Chain**.

Wait for the toast `N candidates registered`. Candidate fields lock.

### 3. Generate voters

1. Set **Count** to `5` (or any value 1–1000).
2. Click **Generate**. Five test key pairs are created.
3. Click **Fund** to transfer 0.01 ETH (gas money) to each voter.
4. Click **Add Voters To Whitelist**.

### 4. Start voting

Scroll to **Stage Control**. Click **Start Voting**. Stage changes to
`ACTIVE`.

### 5. Cast votes

Switch to the **Vote** tab.

**Option A — Manual single vote:**

1. Click **Load JSON** and load `data/exports/voters/voters.json` (or
   paste a key into the field).

2. Click **Load Candidates**.
3. Select a candidate.
4. Click **Cast Vote**.

Wait for the toast `Vote submitted successfully`. The TX Hash and QR
receipt appear.

**Option B — Mass vote (recommended for first run):**

1. Click **From Session** under "Mass Vote (Testing)".
2. Confirm the dialog.
3. Watch the log: voters are processed sequentially, each random vote
   logged with TX hash.

### 6. Finish voting

Return to the **Admin** tab. Click **Finish Voting**. Stage changes to
`FINISHED`.

### 7. Run audit

Switch to the **Audit** tab.

1. **Audit Mode** combo: select **Full Audit**.
2. Click **Run Audit**.

The Security Checks table fills with `PASSED` / `FAILED` / `WARNING`
statuses for all six SEC-checks. The Results table shows vote counts
per candidate and the winner.

### 8. Export results

Click **Export JSON** or **Export CSV** in the Audit tab. Files are
saved to `data/exports/`.

---

## What got saved

After the cycle:

| Artifact | Location |
|---|---|
| Session log     | `data/logs/active/session.log` |
| Exported voters | `data/exports/voters/voters.json` |
| Audit reports   | `data/exports/audit_report.json` / `.csv` |
| Receipt QR      | `data/exports/receipts/<tx_hash>.png` |

---

## Next step

Read the [Quick Tour](quick-tour.md) to explore the rest of the interface.