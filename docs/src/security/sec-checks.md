# Security Invariants Specification (SEC-01..06)

## Analyst Note: Dual-Layer Defense Architecture
In MYCELIUM CORE, security invariants are enforced using a **Dual-Layer Defense** model:

1. **Proactive On-Chain Enforcement:** The `VotingCore.sol` smart contract actively rejects unauthorized transactions using Solidity `require()` statements and custom errors.
2. **Reactive Off-Chain Audit:** The Python `AuditService` independently reconstructs the state by reading immutable event logs (`VoteCast`, `StageChanged`), verifying that the contract behaved exactly as expected.

This duality ensures that even if a logical flaw exists in the contract's state management, the independent event-based audit will flag the discrepancy.

---

## SEC-01: Double Vote Protection

- **Rule:** A voter address cannot cast more than one vote.
- **Proactive On-Chain:** `hasVoted[msg.sender] = true` on execution; `revert AlreadyVoted()` on second attempt.
- **Reactive Audit:** Counts `VoteCast` events per voter address. Any address with count > 1 triggers `FAILED`.
- **Code:** `AuditService._check_double_vote()`

## SEC-02: Whitelist Enforcement

- **Rule:** Only whitelisted addresses can vote.
- **Proactive On-Chain:** `if (!whitelist[msg.sender]) revert NotWhitelisted()`.
- **Reactive Audit:** For every `VoteCast` event, checks `VotingService.is_whitelisted(voter)`. Any non-whitelisted voter triggers `FAILED`.
- **Code:** `AuditService._check_whitelist_enforcement()`

## SEC-03: Stage Enforcement

- **Rule:** Votes can only be cast during the `Active` stage.
- **Proactive On-Chain:** `onlyStage(Stage.Active)` modifier on `castVote()`.
- **Reactive Audit:** Reads `VotingStarted` and `VotingFinished` event block numbers. Verifies all `VoteCast` event block numbers fall within `[start_block, end_block]`.
- **Fallback:** If stage events are unavailable, checks current stage name is `ACTIVE` or `FINISHED` (with `WARNING` status).
- **Code:** `AuditService._check_stage_enforcement()`

## SEC-04: Candidate Validation

- **Rule:** Votes can only be cast for registered candidates.
- **Proactive On-Chain:** `if (!candidates[candidate].registered) revert CandidateNotFound()`.
- **Reactive Audit:** Builds a set of registered candidate addresses from `get_candidates()`. For every `VoteCast` event, checks that `event.candidate` is in this set.
- **Code:** `AuditService._check_candidate_validation()`

## SEC-05: Owner-only Administration

- **Rule:** All administrative actions (add candidates, add voters, change stages) must be performed by the contract owner.
- **Proactive On-Chain:** `onlyOwner` modifier on `addCandidate()`, `addVotersBatch()`, `startVoting()`, `finishVoting()`.
- **Reactive Audit:** Reads `CandidateAdded`, `VoterWhitelisted`, and `StageChanged` events. For each event's transaction, retrieves the TX sender (`tx.from`) and compares against `contract.owner()`. Any mismatch triggers `FAILED`.
- **Code:** `AuditService._check_owner_actions()`

## SEC-06: Vote Count Integrity

- **Rule:** The total number of `VoteCast` events must equal the sum of all candidates' `vote_count` values stored on-chain.
- **Proactive On-Chain:** Implicit — `candidates[candidate].votes += 1` on each `castVote()`.
- **Reactive Audit:** Counts `VoteCast` events independently. Sums `vote_count` from all candidates via `get_candidates()`. Compares the two numbers. Any divergence triggers `FAILED`.
- **Code:** `AuditService._check_vote_count_integrity()`

---

## Audit Mode Availability Matrix
| Invariant Check | Pre-vote Mode | Live Mode | Final Mode | Full Mode |
|---|---|---|---|---|
| Candidate Count (≥2) | Active | — | — | Active |
| Whitelist Populated | Active | — | — | Active |
| Stage Valid for Pre-vote | Active | — | — | Active |
| SEC-01 Double Vote | — | Active | Active | Active |
| SEC-02 Whitelist | — | Active | Active | Active |
| SEC-03 Stage Enforcement | — | — | Active | Active |
| SEC-04 Candidate Validation | — | — | Active | Active |
| SEC-05 Owner Actions | — | — | Active | Active |
| SEC-06 Vote Count Integrity | — | — | Active | Active |