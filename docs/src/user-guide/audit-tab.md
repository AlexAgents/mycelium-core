# Audit Tab

The Audit tab is used by the **Auditor / Researcher** role to verify
election integrity by analyzing on-chain events.

---

## Section 1 — Results

Shows current vote counts. Updates whenever:

- An audit is run.
- The user clicks **Refresh** manually.

| Element | Description |
|---|---|
| **Winner** | Candidate name and party. Shows "Tie: A, B" if tied, "No winner" if no votes. Displays only after stage `FINISHED`. |
| **Candidates table** | Columns: Candidate / Party / Address / Votes. Sorted by votes descending. |
| **Refresh** | Reloads results from chain without running checks. |

---

## Section 2 — Security Checks

The core audit interface.

### Audit Mode selector

Four modes, dynamically enabled / disabled based on contract stage:

| Mode | Enabled in stage | What it runs |
|---|---|---|
| **Full Audit** | FINISHED | All checks (pre + live + final). |
| **Pre-vote Check** | SETUP | Candidate count, whitelist populated, stage valid. |
| **Live Check** | ACTIVE | Double vote, whitelist enforcement. |
| **Final Audit** | FINISHED | Candidate validation, stage enforcement, vote count integrity, owner actions. |

Unavailable modes show "(unavailable)" suffix in the combo and the
**Run Audit** button is disabled.

### Run Audit

Triggers the selected audit mode. Results appear in the checks table:

| Column | Description |
|---|---|
| **Check** | Name (e.g. "Double Vote Protection"). |
| **Status** | Color badge: `PASSED` (green), `FAILED` (red), `WARNING` (yellow), `SKIPPED` (gray). |
| **Details** | Human-readable explanation, including evidence (e.g. "No duplicate voters", "Events=87 OnChain=87"). |

### Summary line

Below the table: `Audit YYYY-MM-DD HH:MM:SS — Passed: N, Failed: K, Total: T`.

---

## Section 3 — Export

Three buttons:

| Button | Output |
|---|---|
| **Copy Report** | Copies full audit report to clipboard as formatted JSON (results + audit checks + winner). |
| **JSON** | Saves full report to `.json` file. |
| **CSV** | Saves report to `.csv` (sections: Results, Winner, Audit). |

All three use a **single source of truth** — `AppController.build_full_report()`.

---

## SEC-checks reference

Detailed specification of all 6 invariants:
[Security Checks SEC-01..06](../security/sec-checks.md).

Quick summary:

| Code | Check | Contract enforcement | Audit verification |
|---|---|---|---|
| SEC-01 | Double Vote Protection | `hasVoted[msg.sender]` | No duplicate `VoteCast.voter` |
| SEC-02 | Whitelist Enforcement | `require(whitelist[msg.sender])` | Each `VoteCast.voter` ∈ `VoterWhitelisted` |
| SEC-03 | Stage Enforcement | `onlyStage(Stage.Active)` | All `VoteCast.blockNumber` ∈ [start, end] |
| SEC-04 | Candidate Validation | `require(candidates[c].registered)` | Each `VoteCast.candidate` ∈ `CandidateAdded` |
| SEC-05 | Owner-only Administration | `onlyOwner` modifier | Admin TX `from` == contract `owner()` |
| SEC-06 | Vote Count Integrity | implicit | `len(VoteCast events) == sum(candidate.vote_count)` |

---

## Typical workflow

1. After stage `FINISHED` (administrator clicked Finish Voting).
2. Open Audit tab.
3. Select **Full Audit**.
4. Click **Run Audit**.
5. Review check statuses.
6. Click **JSON** to save the report for archival.