# Module: AuditService

Event-based election audit. Reads blockchain events independently
from contract state to verify security invariants.

- **File:** `src/core/audit_service.py`
- **Class:** `AuditService`

---

## Public API

### `run_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Full audit — runs all checks.

### `run_pre_vote_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Pre-vote checks: candidate count, whitelist populated, stage valid.

### `run_live_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Live checks: double vote, whitelist enforcement.

### `run_final_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Final checks: all of the above plus candidate validation, stage enforcement, vote count integrity, owner actions.

---

## Results

### `build_results() -> list[Candidate]`
Returns candidates sorted by vote_count descending.

### `detect_winner() -> Optional[dict]`
Returns `{"type": "winner", "candidate": Candidate}`, `{"type": "tie", "candidates": [...]}`, or `None`.

---

## Security Checks (Internal)

| Method | SEC Code | What it verifies |
|---|---|---|
| `_check_double_vote` | SEC-01 | No duplicate VoteCast.voter addresses |
| `_check_whitelist_enforcement` | SEC-02 | Every VoteCast.voter is whitelisted |
| `_check_stage_enforcement` | SEC-03 | All VoteCast blocks within [VotingStarted, VotingFinished] |
| `_check_candidate_validation` | SEC-04 | Every VoteCast.candidate is a registered candidate |
| `_check_owner_actions` | SEC-05 | All admin TX senders match contract owner |
| `_check_vote_count_integrity` | SEC-06 | len(VoteCast events) == sum(candidate.vote_count) |
| `_check_candidate_count` | Pre-vote | >= 2 candidates registered |
| `_check_whitelist_populated` | Pre-vote | Whitelist is not empty |