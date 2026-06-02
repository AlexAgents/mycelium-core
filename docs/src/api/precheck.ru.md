# Модуль: Precheck

Логика предголосовой валидации. Используется `AppController.precheck_vote()`.

- **Файл:** `src/core/precheck.py`

---

## PrecheckStatus (Enum)

| Значение | Смысл |
|---|---|
| `OK` | Все проверки пройдены |
| `INVALID_KEY` | Ключ невалиден |
| `NOT_WHITELISTED` | Адрес не в whitelist |
| `ALREADY_VOTED` | Адрес уже голосовал |
| `INSUFFICIENT_BALANCE` | Баланс ниже минимума для газа (~0.0003 ETH) |
| `NO_CONTRACT` | Контракт не развёрнут |
| `UNKNOWN_ERROR` | Непредвиденная ошибка |

---

## PrecheckResult (frozen dataclass)

| Поле | Тип | Описание |
|---|---|---|
| `status` | `PrecheckStatus` | Результат проверки |
| `address` | `str` | Вычисленный адрес |
| `balance_wei` | `int` | Текущий баланс в Wei |
| `required_wei` | `int` | Минимально необходимый баланс |
| `error_text` | `str` | Детали ошибки |

### Свойство: `is_ok -> bool`
`True` если `status == OK`.