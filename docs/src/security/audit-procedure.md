# Standard Operating Procedure (SOP): Election Audit
Step-by-step guide for Auditors and Researchers to verify a completed voting session using MYCELIUM CORE.

---

## 1. Prerequisites

- Voting stage is strictly `FINISHED` (Administrator has clicked "Finish Voting").
- Application is running with RPC status `CONNECTED`.
- Contract address is visible in the application footer.

---

## 2. Execution Procedure
### Step 2.1: Initialize Audit Module
Navigate to the **Audit** tab in the main window.

### Step 2.2: Select Execution Scope
Choose **Full Audit** from the mode selector. This mode orchestrates all SEC-01 through SEC-06 checks, plus pre-vote structural validations.

### Step 2.3: Trigger Verification
Click **Run Audit**. The system will asynchronously fetch all relevant blockchain events and compute the cryptographic invariants. Wait for the progress bar to complete.

### Step 2.4: Evaluate Security Matrix
Examine the Security Checks table. Interpret the flags as follows:
| Status Flag | Meaning | Required Action |
|---|---|---|
| `PASSED` (green) | Cryptographic invariant holds true | No action needed |
| `FAILED` (red) | Critical invariant violated | Investigate the 'Details' column immediately |
| `WARNING` (yellow) | Could not definitively verify (e.g. missing block metadata) | Check chain data availability |
| `SKIPPED` (gray) | Not applicable in the selected mode | Switch to 'Full Audit' mode |

### Step 2.5: Verify Tally Consistency
In the Results section, verify:

- Candidate vote counts match expectations and off-chain projections.
- The Winner / Tie outcome is correctly derived from the tally.
- Total votes correspond exactly to the number of participating voters in the event logs.

### Step 2.6: Generate Immutable Record
Use one of the three export options to create an immutable audit trail:

- **Copy Report** — JSON to clipboard (for quick sharing).
- **Export JSON** — Generates the complete artifact to a `.json` file.
- **Export CSV** — Generates a structured report with `[Results]`, `[Winner]`, `[Audit]` sections for spreadsheet analysis.

### Step 2.7: Session Archival
Click **New Session** in the application header. The current `session.log` is securely archived to `data/logs/archive/<session_id>/` for future forensics.

---

## 3. Final Auditor Checklist

- [ ] All 6 SEC-checks display the `PASSED` status.
- [ ] Vote count in the Results table mathematically matches the event count in the SEC-06 details.
- [ ] Winner name and party are logically correct based on the tally.
- [ ] No `WARNING` statuses remain unexplained.
- [ ] The exported JSON report is securely saved in the organization's archival storage.
- [ ] The archived session log has been reviewed for any unexpected `ERROR` level entries.