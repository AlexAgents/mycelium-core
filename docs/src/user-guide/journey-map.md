# Customer Journey Map

End-to-end journey through a complete voting cycle in **MYCELIUM CORE**.
Three actors, five phases, one session.

---

## Journey Overview

```text
Phase 1         Phase 2         Phase 3         Phase 4         Phase 5
PREPARE    -->  CONFIGURE  -->  VOTE       -->  AUDIT      -->  ARCHIVE
(Admin)         (Admin)         (Voter)         (Auditor)       (Admin)
```

---

## Phase 1: Prepare (Administrator)

| Step | Action | System Response | Emotion |
|:---|:---|:---|:---|
| 1.1 | Launch application | Geth starts, RPC connects, session created | Neutral |
| 1.2 | Enter admin key | Key validated, balance shown | Confident |
| 1.3 | Fund from Dev | 100 ETH transferred, balance updated | Satisfied |
| 1.4 | Deploy contract | Contract compiled and deployed, address shown | Accomplished |

**Touchpoints:** Admin tab, footer status bar, toast notifications

**Pain points:** Geth startup may take 2-5 seconds. Port 8545 conflict if previous instance running.

**Opportunities:** Auto-deploy option in New Session dialog.

---

## Phase 2: Configure (Administrator)

| Step | Action | System Response | Emotion |
|:---|:---|:---|:---|
| 2.1 | Add candidates (2+) | Candidates staged in local table | Focused |
| 2.2 | Register on-chain | TX sent per candidate, fields locked | Confident |
| 2.3 | Generate voters | Key pairs created, counter updated | Efficient |
| 2.4 | Fund voters | ETH distributed, progress bar active | Patient |
| 2.5 | Add to whitelist | Batch TX sent, counter updated | Ready |
| 2.6 | Start voting | Stage changes to ACTIVE | Accomplished |

**Touchpoints:** Admin tab (all 4 sections), confirmation dialogs, progress bar

**Pain points:** Funding 1000+ voters is slow (sequential nonce). Whitelist TX can fail on large batches.

**Opportunities:** Batch funding optimization. Progress estimation.

---

## Phase 3: Vote (Voter)

| Step | Action | System Response | Emotion |
|:---|:---|:---|:---|
| 3.1 | Enter private key | Address derived, status grid updates | Cautious |
| 3.2 | Check status | Whitelisted YES, Has Voted NO shown | Reassured |
| 3.3 | Load candidates | Radio buttons appear | Deciding |
| 3.4 | Select candidate | Radio button checked | Decided |
| 3.5 | Cast vote | TX submitted, QR receipt shown | Satisfied |
| 3.6 | Save receipt | QR PNG saved to disk | Secure |

**Touchpoints:** Vote tab, status grid, QR receipt, toast

**Pain points:** SEC-06 warning on first key input may confuse users. Private key entry feels risky.

**Opportunities:** Key file drag-and-drop. Voter-friendly status explanations.

---

## Phase 4: Audit (Auditor)

| Step | Action | System Response | Emotion |
|:---|:---|:---|:---|
| 4.1 | Open Audit tab | Results table empty, modes available | Investigative |
| 4.2 | Select Full Audit | Mode description shown | Focused |
| 4.3 | Run audit | 6 SEC-checks executed, table fills | Analytical |
| 4.4 | Review results | PASSED/FAILED badges, winner shown | Informed |
| 4.5 | Export report | JSON/CSV saved to disk | Documented |

**Touchpoints:** Audit tab, StatusBadge colors, export buttons

**Pain points:** SEC-03 may return WARNING if stage events unavailable. Audit terms may be unfamiliar.

**Opportunities:** Audit explanation tooltips. Visual diff between audit runs.

---

## Phase 5: Archive (Administrator)

| Step | Action | System Response | Emotion |
|:---|:---|:---|:---|
| 5.1 | Review results | Winner confirmed in Audit tab | Satisfied |
| 5.2 | Export results | JSON/CSV saved | Documented |
| 5.3 | New Session | Logs archived, UI reset | Ready |
| 5.4 | (Optional) Reset | Chain data deleted, Geth restarted | Clean |

**Touchpoints:** Audit tab export, header buttons, confirmation dialogs

**Pain points:** Reset can fail if Windows holds file locks. Manual cleanup instructions may confuse.

**Opportunities:** Auto-export on session end. One-click "complete cycle" report.

---

## Journey Metrics

| Metric | Target | Actual |
|:---|:---|:---|
| Time from launch to first vote | < 5 minutes | ~3 minutes |
| Steps to deploy + configure | 6 clicks + inputs | 6 |
| Steps to cast single vote | 4 clicks + key input | 4 |
| Steps to complete audit | 2 clicks | 2 |
| Full cycle (5 voters, 3 candidates) | < 10 minutes | ~7 minutes |