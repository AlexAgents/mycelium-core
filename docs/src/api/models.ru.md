# Доменные модели

Объекты передачи данных, используемые между слоями. Логика Web3 отсутствует.

- **Файл:** `src/core/models.py`

---

## ElectionStage (IntEnum)

| Значение | Название |
|---|---|
| 0 | SETUP |
| 1 | ACTIVE |
| 2 | FINISHED |

---

## Candidate (датакласс)

| Поле | Тип | По умолчанию |
|---|---|---|
| `name` | `str` | — |
| `party` | `str` | — |
| `address` | `str` | — |
| `vote_count` | `int` | `0` |
| `registered` | `bool` | `False` |

---

## Voter (датакласс)

| Поле | Тип | По умолчанию |
|---|---|---|
| `address` | `str` | — |
| `private_key` | `Optional[str]` | `None` |
| `has_voted` | `bool` | `False` |

### `to_export_dict() -> dict`

---

## VoteReceipt (датакласс)

| Поле | Тип |
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

## AuditCheck (датакласс)

| Поле | Тип |
|---|---|
| `check_name` | `str` |
| `status` | `str` — `PASSED` / `FAILED` / `WARNING` / `SKIPPED` |
| `details` | `str` |

---

## AuditReport (датакласс)

| Поле | Тип |
|---|---|
| `session_id` | `str` |
| `audit_timestamp` | `datetime` |
| `checks` | `List[AuditCheck]` |

### Свойства: `all_passed`, `passed_count`, `failed_count`
### `to_dict() -> dict`

---

## SessionContext (датакласс)

| Поле | Тип | По умолчанию |
|---|---|---|
| `session_id` | `Optional[str]` | `None` |
| `contract_address` | `Optional[str]` | `None` |
| `candidates` | `List[Candidate]` | `[]` |
| `voters` | `List[Voter]` | `[]` |
| `abi` | `Optional[list]` | `None` |
| `deploy_block` | `int` | `0` |

### `reset() -> None`
### Свойства: `is_deployed`, `candidate_count`, `voter_count`

---

## VoterStatus (неизменяемый датакласс)

| Поле | Тип |
|---|---|
| `key_valid` | `bool` |
| `address` | `str` |
| `is_whitelisted` | `Optional[bool]` |
| `has_voted` | `Optional[bool]` |
| `balance_eth` | `Optional[str]` |
| `stage_name` | `Optional[str]` |
| `error` | `Optional[str]` |

Добавлено в v1.0.1. Все поля типа Optional могут принимать значение `None` при недоступности RPC.