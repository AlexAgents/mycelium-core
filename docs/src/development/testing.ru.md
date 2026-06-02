# Тестирование

MYCELIUM CORE использует `pytest` для автоматических тестов.

Test suite сфокусирован на domain logic, utilities, models, validation, nonce
management, i18n consistency и отдельных service behavior.

---

## Запуск default tests

Из корня приложения:

```bash
cd mycelium-core
python -m pytest -v
```

Default test run исключает integration tests.

---

## Запуск integration tests

```bash
python -m pytest -m integration -v
```

Integration tests могут требовать:

- установленный Solidity compiler;
- internet access для первой установки compiler;
- локальную среду, пригодную для компиляции.

---

## Запуск отдельных test files

### По файлу
```bash
# Audit service
python -m pytest tests/test_audit_service.py -v

# Nonce manager
python -m pytest tests/test_nonce_manager.py -v

# i18n coverage
python -m pytest tests/test_i18n_coverage.py -v

# Voting service helpers
python -m pytest tests/test_voting_service.py -v

# App controller
python -m pytest tests/test_app_controller.py -v
```

### По ключевому слову (быстрая фильтрация)
```bash
# Только тесты парсинга ошибок
python -m pytest -k "error" -v

# Только модели и сессии
python -m pytest -k "model or session" -v

# Только крипто и валидаторы
python -m pytest -k "crypto or validator" -v

# Исключить интеграционные тесты явно
python -m pytest -m "not integration" -v
```

---

## Test areas

| Область | Файлы |
|---|---|
| Models | `tests/test_models.py`, `tests/test_session.py` |
| Validators | `tests/test_validators.py` |
| Crypto utilities | `tests/test_crypto.py` |
| Nonce handling | `tests/test_nonce_manager.py` |
| Error parsing | `tests/test_error_parser.py` |
| Audit logic | `tests/test_audit_service.py` |
| Voting service helpers | `tests/test_voting_service.py` |
| App controller | `tests/test_app_controller.py` |
| i18n consistency | `tests/test_i18n_coverage.py` |
| Compiler integration | `tests/test_compiler.py` |
| Web3 provider | `tests/test_web3_provider.py` |
| Geth manager | `tests/test_geth_manager.py` |
| Precheck logic | `tests/test_precheck.py` |
| Voter status DTO | `tests/test_voter_status.py` |
| QR generation | `tests/test_qr.py` |
| Path utilities | `tests/test_paths.py` |
| Configuration | `tests/test_config.py` |

---

## Integration marker

Тесты компилятора и полного lifecycle помечены как `integration`.
Конфигурация pytest по умолчанию требует строгих маркеров:

```ini
addopts = --strict-markers
```

Интеграционные тесты требуют бинарника Geth в `bin/` и интернет-доступа
для первой загрузки компилятора Solidity. По умолчанию исключены —
запускаются явно:

```bash
python -m pytest -m integration -v
```

---

## Проверки документации

Из корня документации:

```bash
cd docs
mkdocs build --strict
```

---

## Recommended pre-release checklist

```bash
# 1. Проверить сборку документации без ошибок
cd docs
mkdocs build --strict

# 2. Запустить unit-тесты
cd ../mycelium-core
python -m pytest -v

# 3. Запустить интеграционные тесты (требуется бинарник Geth)
python -m pytest -m integration -v
```

---

## Текущий scope

Текущие автоматические тесты покрывают unit-level и выбранную
integration-level логику.

**Текущий статус: 180 тестов пройдено** за ~100 секунд (включая полный
интеграционный тест жизненного цикла с реальным узлом Geth).

Полное UI E2E тестирование в этой версии не реализовано.