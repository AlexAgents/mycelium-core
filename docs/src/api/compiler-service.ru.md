# Модуль: CompilerService

Компиляция Solidity-контрактов через `py-solc-x`.

- **Файл:** `src/core/compiler_service.py`
- **Класс:** `CompilerService`

---

## Методы

### `compile_contract() -> tuple[list, str]`
Компилирует `contracts/VotingCore.sol`. Устанавливает solc при необходимости.
Возвращает `(abi, bytecode)`.
Генерирует `FileNotFoundError`, если файл контракта отсутствует.

### `load_artifacts() -> tuple[list, str]`
Загружает ранее скомпилированные ABI и байт-код из `contracts/abi/VotingCore.json`.
Генерирует `FileNotFoundError`, если артефакт отсутствует.

---

## Внутренние методы

### `_save_artifacts(abi, bytecode) -> None`
Сохраняет ABI и байт-код в `contracts/abi/VotingCore.json`.