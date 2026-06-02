# Module: Web3Provider

Singleton RPC connection to the Ethereum node.

- **File:** `src/core/web3_provider.py`
- **Class:** `Web3Provider`

---

## Connection

### `connect() -> None`
Creates `Web3(HTTPProvider(rpc_url))` and injects POA middleware.

### `wait_for_rpc(timeout: int = 30) -> bool`
Polls connection every 0.5s until connected or timeout. Returns `True` on success.

### `is_connected() -> bool`
### `ping() -> bool`
Safe version — does not raise if not connected.

---

## Diagnostics

### `client_version() -> str`
Returns Geth version string. Returns `"unknown"` if not connected.

---

## Blockchain Info

### `get_block_number() -> Optional[int]`
### `get_chain_id() -> int`
### `get_accounts() -> list[str]`
### `get_balance(address: str) -> int`

---

## Contracts

### `get_contract(address: str, abi: list)`
Returns a Web3 contract instance.

### `validate_abi_hash(abi: list, expected_hash: str) -> bool`
Compares SHA-256 hash of serialized ABI against expected. Returns `True` if matching or hash is empty.

---

## Raw Access

### `w3 -> Web3` (property)
Raises `RuntimeError` if not connected.