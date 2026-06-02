# Модуль: AppController

Главный фасад между UI и доменными сервисами. Вкладки UI никогда
не импортируют `web3`, `eth_account` или `solcx` — они вызывают
исключительно методы `AppController`.

- **Файл:** `src/core/app_controller.py`
- **Класс:** `AppController`

---

## Жизненный цикл

### `startup() -> None`
Запускает Geth, подключает Web3Provider, ожидает готовности RPC.
Генерирует `RuntimeError`, если RPC недоступен после таймаута.

### `shutdown() -> None`
Архивирует лог сессии, останавливает Geth. Вызывается из `MainWindow.closeEvent`.

### `create_session(title: str = "MYCELIUM Session") -> str`
Сбрасывает контекст сессии, генерирует новый UUID. Возвращает session ID.

### `new_session() -> str`
Архивирует текущий лог сессии, создаёт новую. Возвращает новый session ID.

### `get_session_summary() -> dict`
Возвращает `{session_id, contract_address, candidate_count, voter_count}`.

---

## Компиляция / Деплой

### `compile_contract() -> None`
Компилирует `VotingCore.sol` через `CompilerService`. Сохраняет ABI и байт-код в сессии.

### `deploy_contract(admin_private_key: str) -> str`
Разворачивает скомпилированный контракт. Возвращает адрес контракта.
Генерирует `RuntimeError`, если контракт не скомпилирован.

---

## Кандидаты

### `add_candidate(admin_private_key: str, name: str, party: str, address: str) -> str`
Регистрирует кандидата on-chain. Возвращает TX hash.

---

## Избиратели

### `generate_voters(count: int) -> list[Voter]`
Генерирует тестовые пары ключей. Добавляет к избирателям сессии. Возвращает список `Voter`.

### `whitelist_voters(admin_private_key: str) -> str`
Отправляет транзакцию `addVotersBatch` со всеми адресами избирателей сессии. Возвращает TX hash.

### `export_voters(output_path: str) -> None`
Экспортирует избирателей в JSON (содержит приватные ключи). Показывает предупреждение
безопасности в UI.

### `import_voters(input_path: str) -> int`
Загружает избирателей из JSON-файла. Возвращает количество импортированных.

---

## Финансирование

### `fund_voter(admin_private_key: str, voter_address: str, amount_wei: int) -> str`
Переводит ETH от admin одному избирателю. Возвращает TX hash.

### `fund_from_dev(target_address: str, amount_eth: float = 100.0) -> str`
Переводит ETH с разблокированного dev-аккаунта Geth. Только dev-режим.
Генерирует `RuntimeError`, если не dev-режим или dev-аккаунт недоступен.

---

## Баланс

### `get_balance_wei(address: str) -> int`
Возвращает необработанный баланс в Wei.

### `get_balance_eth(address: str) -> str`
Возвращает форматированную строку баланса. Адаптивный формат: `"0"`, `"1.2345"`,
`"100.00K"`, `"1.23T"`, `"1.16e+59"`.

### `get_dev_account_address() -> Optional[str]`
Возвращает первый адрес из `eth.accounts` (dev-аккаунт Geth) или `None`.

---

## Ключевые утилиты

### `get_address_from_key(private_key: str) -> str`
Вычисляет Ethereum-адрес из приватного ключа. UI никогда не импортирует `eth_account` напрямую.

### `validate_private_key(key: str) -> bool`
Возвращает `True`, если ключ является валидным Ethereum-ключом.

---

## Стадии

### `check_start_voting_ready() -> tuple[bool, str]`
Предпроверка перед запуском. Возвращает `(ready, reason_key)`. Проверяет: контракт развёрнут,
≥2 кандидата, whitelist не пуст.

### `start_voting(admin_private_key: str) -> str`
Вызывает `startVoting()` на контракте. Возвращает TX hash.

### `finish_voting(admin_private_key: str) -> str`
Вызывает `finishVoting()` на контракте. Возвращает TX hash.

---

## Голосование

### `cast_vote(voter_private_key: str, candidate_address: str) -> VoteReceipt`
Отправляет транзакцию `castVote`. Возвращает `VoteReceipt` с TX hash, номером блока и QR-байтами.
Генерирует `RuntimeError`, если нет активной сессии.

### `precheck_vote(voter_private_key: str, min_balance_wei: int = 300_000_000_000_000) -> PrecheckResult`
5-уровневая валидация: валидность ключа → контракт развёрнут → в whitelist → has_voted → баланс.
Возвращает `PrecheckResult`. UI показывает переведённый диалог для каждого статуса ошибки.

---

## Статус избирателя

### `get_voter_status(private_key: str) -> VoterStatus`
Агрегированный снимок состояния: key_valid, address, is_whitelisted, has_voted, balance_eth,
stage_name. Все поля `Optional` — UI обрабатывает `None` корректно.
Добавлен в v1.0.1 для устранения синхронных RPC-вызовов из потока UI.

---

## Аудит

### `run_audit() -> AuditReport`
Запускает полный аудит. Возвращает `AuditReport` со списком проверок.

### `get_results() -> list[Candidate]`
Возвращает кандидатов, отсортированных по количеству голосов по убыванию.

### `get_winner() -> Optional[dict]`
Возвращает `{"type": "winner", "candidate": Candidate}`, `{"type": "tie", "candidates": [...]}` или
`None`.

### `build_full_report() -> dict`
Единственный источник истины для Copy Report / JSON / CSV экспорта. Содержит метаданные
сессии, результаты, победителя и проверки аудита.

### `export_results(output_path: str) -> None`
Экспортирует полный отчёт в JSON-файл.

### `export_results_csv(output_path: str) -> None`
Экспортирует полный отчёт в CSV с разделами: `[Results]`, `[Winner]`, `[Audit]`.

---

## Парсинг ошибок

### `parse_rpc_error(error_text: str) -> dict`
Делегирует в `ErrorParser`. Возвращает `{message_key, raw_message, action_key, action_id}`.
UI вызывает `t(message_key)` для локализованного отображения.

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

Возвращает `{size_bytes, size_mb, deployed_contracts, archived_sessions}`.

---

## Сброс блокчейна

### `reset_blockchain_data(delete_archived_logs: bool = False) -> None`
Останавливает Geth, удаляет chain-data с повторными попытками (файловые блокировки Windows),
перезапускает Geth, создаёт новую сессию.
Генерирует `RuntimeError` с `MANUAL_CLEANUP_REQUIRED|paths`, если файлы заблокированы.