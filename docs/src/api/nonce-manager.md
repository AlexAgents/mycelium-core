# Module: NonceManager

Thread-safe nonce tracking for a single Ethereum account.

- **File:** `src/core/nonce_manager.py`
- **Class:** `NonceManager`

---

## Constructor

### `__init__(w3: Web3, address: str)`
Initializes with a Web3 instance and checksummed address.

---

## Methods

### `get_next_nonce() -> int`
Returns the next available nonce. Fetches from network on first call, then increments internally.
Thread-safe via `threading.Lock`.

### `sync() -> None`
Re-fetches the pending nonce from the network. Call after transaction errors.

### `reset() -> None`
Clears internal state. Used on account change or new session.