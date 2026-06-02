# Модуль: VotingService

Инкапсулирует всю логику блокчейн-транзакций. UI никогда не взаимодействует
с этим классом напрямую — только через `AppController`.

- **Файл:** `src/core/voting_service.py`
- **Класс:** `VotingService`

---

## Конструктор

### `__init__(provider: Web3Provider)`
Инициализируется со ссылкой на Web3Provider. Управляет внутренними менеджерами nonce для каждого аккаунта.

---

## Управление контрактом

### `load_contract(contract_address: str, abi: list) -> None`
Загружает уже развёрнутый контракт по адресу и ABI для последующих вызовов.

### `reset() -> None`
Сбрасывает ссылку на контракт, ABI, байткод и все менеджеры nonce. Вызывается при создании новой сессии.

---

## Развёртывание

### `deploy_contract(admin_private_key: str, abi: list, bytecode: str) -> str`
Формирует и отправляет транзакцию создания контракта. Ожидает получения квитанции.
Возвращает адрес развёрнутого контракта.
Генерирует `RuntimeError`, если в квитанции отсутствует адрес контракта.

---

## Перевод ETH

### `fund_account(sender_private_key: str, target_address: str, amount_wei: int) -> str`
Отправляет ETH от отправителя получателю. Не требует развёрнутого контракта.
Возвращает хэш транзакции.

---

## Управление кандидатами

### `add_candidate(admin_private_key: str, candidate: Candidate) -> str`
Вызывает `addCandidate(name, party, address)` на контракте.
Возвращает хэш транзакции.

---

## Whitelist

### `add_voters_batch(admin_private_key: str, voters: list[str]) -> str`
Вызывает `addVotersBatch(addresses)` на контракте.
Возвращает хэш транзакции.

---

## Управление стадиями

### `start_voting(admin_private_key: str) -> str`
Вызывает `startVoting()`. Возвращает хэш транзакции.

### `finish_voting(admin_private_key: str) -> str`
Вызывает `finishVoting()`. Возвращает хэш транзакции.

---

## Голосование

### `cast_vote(voter_private_key: str, candidate_address: str, session_id: str) -> VoteReceipt`
Вызывает `castVote(candidate)`. Формирует QR-квитанцию.
Возвращает `VoteReceipt` с полями tx_hash, block_number, qr_bytes.

---

## API чтения

### `get_stage() -> ElectionStage`
### `has_voted(address: str) -> bool`
### `is_whitelisted(address: str) -> bool`
### `get_candidates() -> list[Candidate]`
### `get_owner() -> str`

---

## Внутренний механизм: отправка транзакций

### `_send_transaction(tx: dict, private_key: str)`
Подписывает и транслирует транзакцию с логикой повторных попыток:

- **ContractLogicError:** Разбирает причину отката, повторные попытки **не выполняются**.
- **TimeExhausted:** Синхронизирует nonce, повторные попытки **не выполняются** (транзакция может находиться в ожидании).
- **ValueError (nonce too low / already known):** Синхронизирует nonce и пересобирает транзакцию, до 3 повторных попыток с экспоненциальной выдержкой.
- **Insufficient funds:** Синхронизирует nonce, генерирует исключение с понятным сообщением.

### `_humanize_contract_error(error_text: str) -> str`
Сопоставляет названия ошибок контракта (`NotWhitelisted`, `AlreadyVoted`, `CandidateNotFound`, `InvalidStage`, `Unauthorized`) с понятными пользователю сообщениями.