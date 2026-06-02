# Module: GethManager

Manages the local Geth process lifecycle.

- **File:** `src/core/geth_manager.py`
- **Class:** `GethManager`

---

## Properties

### `mode -> str`
Returns `"dev"` (standard `--dev` mode) or `"custom"`.

### `rpc_url -> str`
Returns `http://{rpc_host}:{rpc_port}`.

---

## Lifecycle

### `start() -> None`

1. Checks `geth.exe` exists in `bin/`.
2. Kills zombie geth processes (`taskkill`).
3. Cleans `chain-data/active/` (dev mode incompatible with persistent data).
4. Checks port 8545 availability.
5. Spawns Geth subprocess with `--dev --dev.period 5`.
6. Starts monitor thread.

Raises `FileNotFoundError` if Geth binary missing.
Raises `RuntimeError` if port occupied after cleanup.

### `stop() -> None`
Sets `_shutting_down = True` before terminate to prevent false crash callbacks.
Graceful terminate → kill → force taskkill → close log file handle.

### `is_running() -> bool`
Returns `True` if process is alive.

---

## Chain Data

### `purge_chain_data(archive: bool = True) -> None`
Archives or deletes `chain-data/active/`. Kills zombie processes, recreates empty directory.

---

## Crash Monitoring

### `set_crash_callback(cb: Callable) -> None`
Registers a callback invoked when Geth dies unexpectedly (not during intentional shutdown).
The monitor thread checks `_shutting_down` flag to distinguish crashes from normal stops.