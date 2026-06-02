# Module: VotingService

Encapsulates all blockchain transaction logic. UI never interacts
with this class directly — only through `AppController`.

- **File:** `src/core/voting_service.py`
- **Class:** `VotingService`

---

## Constructor

### `__init__(provider: Web3Provider)`
Initializes with a Web3Provider reference. Manages internal nonce managers per account.

---

## Contract Management

### `load_contract(contract_address: str, abi: list) -> None`
Loads an already-deployed contract by address and ABI for subsequent calls.

### `reset() -> None`
Clears contract reference, ABI, bytecode, and all nonce managers. Called on new session.

---

## Deploy

### `deploy_contract(admin_private_key: str, abi: list, bytecode: str) -> str`
Builds and sends a contract creation transaction. Waits for receipt.
Returns the deployed contract address.
Raises `RuntimeError` if no contract address in receipt.

---

## ETH Transfer

### `fund_account(sender_private_key: str, target_address: str, amount_wei: int) -> str`
Sends ETH from sender to target. Does not require a deployed contract.
Returns TX hash.

---

## Candidate Management

### `add_candidate(admin_private_key: str, candidate: Candidate) -> str`
Calls `addCandidate(name, party, address)` on the contract.
Returns TX hash.

---

## Whitelist

### `add_voters_batch(admin_private_key: str, voters: list[str]) -> str`
Calls `addVotersBatch(addresses)` on the contract.
Returns TX hash.

---

## Stage Control

### `start_voting(admin_private_key: str) -> str`
Calls `startVoting()`. Returns TX hash.

### `finish_voting(admin_private_key: str) -> str`
Calls `finishVoting()`. Returns TX hash.

---

## Voting

### `cast_vote(voter_private_key: str, candidate_address: str, session_id: str) -> VoteReceipt`
Calls `castVote(candidate)`. Generates QR receipt.
Returns `VoteReceipt` with tx_hash, block_number, qr_bytes.

---

## Read API

### `get_stage() -> ElectionStage`
### `has_voted(address: str) -> bool`
### `is_whitelisted(address: str) -> bool`
### `get_candidates() -> list[Candidate]`
### `get_owner() -> str`

---

## Internal: Transaction Sender

### `_send_transaction(tx: dict, private_key: str)`
Signs and broadcasts a transaction with retry logic:

- **ContractLogicError:** Parses revert reason, does NOT retry.
- **TimeExhausted:** Syncs nonce, does NOT retry (TX may be pending).
- **ValueError (nonce too low / already known):** Syncs nonce + rebuilds TX, up to 3 retries with exponential backoff.
- **Insufficient funds:** Syncs nonce, raises with clear message.

### `_humanize_contract_error(error_text: str) -> str`
Maps contract error names (`NotWhitelisted`, `AlreadyVoted`, `CandidateNotFound`, `InvalidStage`, `Unauthorized`) to human-readable messages.