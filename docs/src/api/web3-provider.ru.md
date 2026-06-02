# Модуль: Web3Provider

Одиночное RPC-соединение с узлом Ethereum.

- **Файл:** `src/core/web3_provider.py`
- **Класс:** `Web3Provider`

---

## Подключение

### `connect() -> None`
Создаёт `Web3(HTTPProvider(rpc_url))` и подключает middleware для POA.

### `wait_for_rpc(timeout: int = 30) -> bool`
Опрашивает соединение каждые 0,5 с до успешного подключения или истечения таймаута. Возвращает `True` в случае успеха.

### `is_connected() -> bool`
### `ping() -> bool`
Безопасная версия — не генерирует исключение при отсутствии соединения.

---

## Диагностика

### `client_version() -> str`
Возвращает строку с версией Geth. Возвращает `"unknown"` при отсутствии соединения.

---

## Информация о блокчейне

### `get_block_number() -> Optional[int]`
### `get_chain_id() -> int`
### `get_accounts() -> list[str]`
### `get_balance(address: str) -> int`

---

## Контракты

### `get_contract(address: str, abi: list)`
Возвращает экземпляр контракта Web3.

### `validate_abi_hash(abi: list, expected_hash: str) -> bool`
Сравнивает SHA-256 хэш сериализованного ABI с ожидаемым значением. Возвращает `True`, если хэши совпадают или ожидаемый хэш пуст.

---

## Прямой доступ

### `w3 -> Web3` (свойство)
Генерирует `RuntimeError` при отсутствии соединения.