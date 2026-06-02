# Module: Precheck

Pre-vote validation logic. Used by `AppController.precheck_vote()`.

- **File:** `src/core/precheck.py`

---

## PrecheckStatus (Enum)

| Value | Meaning |
|---|---|
| `OK` | All checks passed — safe to send transaction |
| `INVALID_KEY` | Private key is malformed or invalid |
| `NOT_WHITELISTED` | Address not in the contract whitelist |
| `ALREADY_VOTED` | Address has already cast a vote |
| `INSUFFICIENT_BALANCE` | Balance below minimum gas requirement (~0.0003 ETH) |
| `NO_CONTRACT` | No contract deployed in current session |
| `UNKNOWN_ERROR` | Unexpected RPC or validation error |

---

## PrecheckResult (frozen dataclass)

| Field | Type | Description |
|---|---|---|
| `status` | `PrecheckStatus` | Result of the check |
| `address` | `str` | Derived Ethereum address (empty if key invalid) |
| `balance_wei` | `int` | Current balance in Wei |
| `required_wei` | `int` | Minimum required balance |
| `error_text` | `str` | Error details (for UNKNOWN_ERROR) |

### Property: `is_ok -> bool`
Returns `True` if `status == PrecheckStatus.OK`.