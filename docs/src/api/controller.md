# Module: AppController

The primary Facade between UI and domain services. UI tabs never
import `web3`, `eth_account`, or `solcx` — they call `AppController`
methods exclusively.

- **File:** `src/core/app_controller.py`
- **Class:** `AppController`

---

## Lifecycle

### `startup() -> None`
Starts Geth, connects Web3Provider, waits for RPC readiness.
Raises `RuntimeError` if RPC is unavailable after timeout.

### `shutdown() -> None`
Archives session log, stops Geth. Called from `MainWindow.closeEvent`.

### `create_session(title: str = "MYCELIUM Session") -> str`
Resets session context, generates new UUID. Returns session ID.

### `new_session() -> str`
Archives current session log, creates a fresh session. Returns new session ID.

### `get_session_summary() -> dict`
Returns `{session_id, contract_address, candidate_count, voter_count}`.

---

## Compile / Deploy

### `compile_contract() -> None`
Compiles `VotingCore.sol` via `CompilerService`. Stores ABI and bytecode in session.

### `deploy_contract(admin_private_key: str) -> str`
Deploys the compiled contract. Returns contract address.
Raises `RuntimeError` if contract not compiled.

---

## Candidates

### `add_candidate(admin_private_key: str, name: str, party: str, address: str) -> str`
Registers one candidate on-chain. Returns TX hash.

---

## Voters

### `generate_voters(count: int) -> list[Voter]`
Generates `count` test key pairs. Appends to session voters. Returns list of `Voter`.

### `whitelist_voters(admin_private_key: str) -> str`
Sends `addVotersBatch` transaction with all session voter addresses. Returns TX hash.

### `export_voters(output_path: str) -> None`
Exports voters to JSON (includes private keys). Shows security warning in UI.

### `import_voters(input_path: str) -> int`
Loads voters from JSON file. Returns count of imported voters.

---

## Funding

### `fund_voter(admin_private_key: str, voter_address: str, amount_wei: int) -> str`
Transfers ETH from admin to a single voter. Returns TX hash.

### `fund_from_dev(target_address: str, amount_eth: float = 100.0) -> str`
Transfers ETH from the unlocked Geth dev account. Dev mode only.
Raises `RuntimeError` if not in dev mode or no dev account.

---

## Balance

### `get_balance_wei(address: str) -> int`
Returns raw balance in Wei.

### `get_balance_eth(address: str) -> str`
Returns formatted balance string. Adaptive format: `"0"`, `"1.2345"`, `"100.00K"`, `"1.23T"`, `"1.16e+59"`.

### `get_dev_account_address() -> Optional[str]`
Returns the first `eth.accounts` address (Geth dev account) or `None`.

---

## Key Utilities

### `get_address_from_key(private_key: str) -> str`
Derives Ethereum address from a private key. UI never imports `eth_account` directly.

### `validate_private_key(key: str) -> bool`
Returns `True` if the key is a valid Ethereum private key.

---

## Stages

### `check_start_voting_ready() -> tuple[bool, str]`
Pre-flight check. Returns `(ready, reason_key)`. Validates: contract deployed, ≥2 candidates, whitelist not empty.

### `start_voting(admin_private_key: str) -> str`
Calls `startVoting()` on the contract. Returns TX hash.

### `finish_voting(admin_private_key: str) -> str`
Calls `finishVoting()` on the contract. Returns TX hash.

---

## Voting

### `cast_vote(voter_private_key: str, candidate_address: str) -> VoteReceipt`
Sends a `castVote` transaction. Returns `VoteReceipt` with TX hash, block number, and QR bytes.
Raises `RuntimeError` if no active session.

### `precheck_vote(voter_private_key: str, min_balance_wei: int = 300_000_000_000_000) -> PrecheckResult`
5-level validation: key validity → contract deployed → whitelisted → has_voted → balance.
Returns `PrecheckResult`. UI shows translated dialog for each failure status.

---

## Voter Status

### `get_voter_status(private_key: str) -> VoterStatus`
Aggregated snapshot: key_valid, address, is_whitelisted, has_voted, balance_eth, stage_name.
All fields are `Optional` — UI handles `None` gracefully.
Added in v1.0.1 to eliminate synchronous RPC calls from the UI thread.

---

## Audit

### `run_audit() -> AuditReport`
Runs full audit. Returns `AuditReport` with checks list.

### `get_results() -> list[Candidate]`
Returns candidates sorted by vote count descending.

### `get_winner() -> Optional[dict]`
Returns `{"type": "winner", "candidate": Candidate}` or `{"type": "tie", "candidates": [...]}` or `None`.

### `build_full_report() -> dict`
Single source of truth for Copy Report / JSON / CSV export. Contains session metadata, results, winner, and audit checks.

### `export_results(output_path: str) -> None`
Exports full report to JSON file.

### `export_results_csv(output_path: str) -> None`
Exports full report to CSV with sections: `[Results]`, `[Winner]`, `[Audit]`.

---

## Error Parsing

### `parse_rpc_error(error_text: str) -> dict`
Delegates to `ErrorParser`. Returns `{message_key, raw_message, action_key, action_id}`.
UI calls `t(message_key)` for localized display.

---

## Read API

### `get_stage() -> ElectionStage`
### `get_candidates() -> list[Candidate]`
### `is_whitelisted(address: str) -> bool`
### `has_voted(address: str) -> bool`
### `get_rpc_status() -> bool`
### `get_block_number() -> Optional[int]`
### `get_client_version() -> str`
### `is_contract_deployed() -> bool`
### `get_contract_address() -> Optional[str]`
### `is_dev_mode() -> bool`
### `get_geth_mode() -> str`
### `get_chain_stats() -> dict`

Returns `{size_bytes, size_mb, deployed_contracts, archived_sessions}`.

---

## Blockchain Reset

### `reset_blockchain_data(delete_archived_logs: bool = False) -> None`
Stops Geth, deletes chain-data with retry (Windows file locks), restarts Geth, creates new session.
Raises `RuntimeError` with `MANUAL_CLEANUP_REQUIRED|paths` if files are locked.