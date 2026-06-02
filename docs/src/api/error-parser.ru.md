# Модуль: ErrorParser

Преобразует необработанные ошибки RPC и контракта в структурированные
результаты с i18n-ключами. Бизнес-логика — не зависит от Qt или UI.

- **Файл:** `src/core/error_parser.py`
- **Классы:** `ErrorParser`, `ParsedError`

---

## ParsedError (неизменяемый датакласс)

| Поле | Тип | Описание |
|---|---|---|
| `message_key` | `Optional[str]` | i18n-ключ основного сообщения или `None`, если шаблон не распознан |
| `raw_message` | `str` | Исходный текст ошибки (запасной вариант) |
| `action_key` | `Optional[str]` | i18n-ключ текста кнопки действия |
| `action_id` | `Optional[str]` | Машинный идентификатор обработчика действия в UI |

---

## ErrorParser.parse(error_text: str) -> ParsedError

Распознаваемые шаблоны:

| Шаблон | message_key | action_id |
|---|---|---|
| `insufficient funds` | `err.parser.insufficient_funds` | `fund_account` |
| `nonce too low` / `already known` | `err.parser.nonce_conflict` | `sync_nonce` |
| `timeout` / `timed out` | `err.parser.timeout` | `check_status` |
| `NotWhitelisted` | `err.parser.not_whitelisted` | — |
| `AlreadyVoted` | `err.parser.already_voted` | — |
| `CandidateNotFound` | `err.parser.candidate_not_found` | — |
| `InvalidStage` | `err.parser.invalid_stage` | — |
| `Unauthorized` | `err.parser.unauthorized` | — |
| `execution reverted` (общий) | `err.parser.contract_reverted` | — |
| Нераспознанный | `None` | — |