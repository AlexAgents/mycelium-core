# Domain Models

Data Transfer Objects used between layers. No Web3 logic.

- **File:** `src/core/models.py`

---

## ElectionStage (IntEnum)

| Value | Name |
|---|---|
| 0 | SETUP |
| 1 | ACTIVE |
| 2 | FINISHED |

---

## Candidate (dataclass)

| Field | Type | Default |
|---|---|---|
| `name` | `str` | — |
| `party` | `str` | — |
| `address` | `str` | — |
| `vote_count` | `int` | `0` |
| `registered` | `bool` | `False` |

---

## Voter (dataclass)

| Field | Type | Default |
|---|---|---|
| `address` | `str` | — |
| `private_key` | `Optional[str]` | `None` |
| `has_voted` | `bool` | `False` |

### `to_export_dict() -> dict`

---

## VoteReceipt (dataclass)

| Field | Type |
|---|---|
| `tx_hash` | `str` |
| `voter_address` | `str` |
| `candidate_address` | `str` |
| `block_number` | `int` |
| `session_id` | `str` |
| `timestamp` | `datetime` |
| `qr_bytes` | `Optional[bytes]` |

### `to_dict() -> dict`

---

## AuditCheck (dataclass)

| Field | Type |
|---|---|
| `check_name` | `str` |
| `status` | `str` — `PASSED` / `FAILED` / `WARNING` / `SKIPPED` |
| `details` | `str` |

---

## AuditReport (dataclass)

| Field | Type |
|---|---|
| `session_id` | `str` |
| `audit_timestamp` | `datetime` |
| `checks` | `List[AuditCheck]` |

### Properties: `all_passed`, `passed_count`, `failed_count`
### `to_dict() -> dict`

---

## SessionContext (dataclass)

| Field | Type | Default |
|---|---|---|
| `session_id` | `Optional[str]` | `None` |
| `contract_address` | `Optional[str]` | `None` |
| `candidates` | `List[Candidate]` | `[]` |
| `voters` | `List[Voter]` | `[]` |
| `abi` | `Optional[list]` | `None` |
| `deploy_block` | `int` | `0` |

### `reset() -> None`
### Properties: `is_deployed`, `candidate_count`, `voter_count`

---

## VoterStatus (frozen dataclass)

| Field | Type |
|---|---|
| `key_valid` | `bool` |
| `address` | `str` |
| `is_whitelisted` | `Optional[bool]` |
| `has_voted` | `Optional[bool]` |
| `balance_eth` | `Optional[str]` |
| `stage_name` | `Optional[str]` |
| `error` | `Optional[str]` |

Added in v1.0.1. All Optional fields may be `None` if RPC unavailable.