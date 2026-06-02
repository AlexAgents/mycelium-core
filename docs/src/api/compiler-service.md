# Module: CompilerService

Solidity contract compilation via `py-solc-x`.

- **File:** `src/core/compiler_service.py`
- **Class:** `CompilerService`

---

## Methods

### `compile_contract() -> tuple[list, str]`
Compiles `contracts/VotingCore.sol`. Installs solc if needed.
Returns `(abi, bytecode)`.
Raises `FileNotFoundError` if contract file missing.

### `load_artifacts() -> tuple[list, str]`
Loads previously compiled ABI and bytecode from `contracts/abi/VotingCore.json`.
Raises `FileNotFoundError` if artifact missing.

---

## Internal

### `_save_artifacts(abi, bytecode) -> None`
Saves ABI + bytecode to `contracts/abi/VotingCore.json`.