# Module: ErrorParser

Translates raw RPC and contract errors into structured i18n-keyed
results. Business logic — does not depend on Qt or UI.

- **File:** `src/core/error_parser.py`
- **Classes:** `ErrorParser`, `ParsedError`

---

## ParsedError (frozen dataclass)

| Field | Type | Description |
|---|---|---|
| `message_key` | `Optional[str]` | i18n key for the main message, or `None` if unrecognized |
| `raw_message` | `str` | Original error text (fallback) |
| `action_key` | `Optional[str]` | i18n key for action button text |
| `action_id` | `Optional[str]` | Machine ID for the action handler in UI |

---

## ErrorParser.parse(error_text: str) -> ParsedError

Recognized patterns:

| Pattern | message_key | action_id |
|---|---|---|
| `insufficient funds` | `err.parser.insufficient_funds` | `fund_account` |
| `nonce too low` / `already known` | `err.parser.nonce_conflict` | `sync_nonce` |
| `timeout` / `timed out` | `err.parser.timeout` | `check_status` |
| `NotWhitelisted` | `err.parser.not_whitelisted` | — |
| `AlreadyVoted` | `err.parser.already_voted` | — |
| `CandidateNotFound` | `err.parser.candidate_not_found` | — |
| `InvalidStage` | `err.parser.invalid_stage` | — |
| `Unauthorized` | `err.parser.unauthorized` | — |
| `execution reverted` (generic) | `err.parser.contract_reverted` | — |
| Unrecognized | `None` | — |