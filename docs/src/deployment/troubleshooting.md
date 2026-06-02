# Troubleshooting

Solutions to common issues encountered when running **MYCELIUM CORE**.

---

## Geth & Network

### Port 8545 is already in use
```bash
taskkill /F /IM geth.exe /T
```
Then restart the application. If still occupied, another process is using the port — change `RPC_PORT` in `.env`.

### "Geth not found" error
Verify `bin/geth.exe` (Windows) or `bin/geth` (Linux/macOS) exists and has execute permissions.

### Geth starts but RPC never connects
Check `data/chain-data/active/geth.log` for error messages. Common cause: corrupted chain-data. Solution: click **Reset Data** in the header or delete `data/chain-data/active/` manually.

### Geth crashes immediately after start
The chain-data directory may be corrupted from a previous unclean shutdown. Delete `data/chain-data/active/` and restart.

### Blocks are not being mined
Geth `--dev` with `--dev.period 5` mines a block every 5 seconds regardless of pending transactions. If blocks stop incrementing, Geth has likely crashed — check the footer status badge.

---

## Contract & Transactions

### "Contract not compiled" error on deploy
The application compiles `contracts/VotingCore.sol` on the fly. Ensure the file exists and is not corrupted. The Solidity compiler is downloaded automatically by `py-solc-x` on first use — ensure internet access.

### "Insufficient funds for gas"
Your admin or voter account has no ETH. For admin: click **Fund from Dev**. For voters: click **Fund** in the Voters section.

### "Nonce too low" error
The nonce tracker is out of sync. The application retries automatically (up to 3 times with backoff). If persistent, create a **New Session**.

### Deploy button stays disabled
Deploy is disabled after a successful deployment to prevent accidental re-deploy. Create a **New Session** to deploy again.

### Transaction confirmation timeout
The transaction was broadcast but not mined within 120 seconds. Check if Geth is still running. The transaction may still be pending in the mempool.

---

## UI & Application

### Application window does not appear
Run from terminal to see error output: `python main.py`. Common causes: missing PyQt6, missing dependencies, Python version mismatch.

### Language does not fully change
Some labels require an application restart for complete translation. This is noted in the language-switch toast notification.

### Toast notifications appear behind other windows
Fixed in v1.0.0. Toasts are rendered as children of the central widget. If this still occurs, ensure you are running the latest version.

### Logs tab shows "(log file not found)"
The log file is created on application startup. If the file is missing, the application may not have started correctly. Check terminal output.

### Theme switch does not update status badges
Fixed in v1.0.0. All `StatusBadge` widgets call `refresh_theme()` on theme change. If badges appear wrong, click the theme button twice.

---

## Tests

### `ModuleNotFoundError: src` when running pytest
Ensure you are running from the project root with `pytest.ini` present. The file sets `pythonpath = .` which adds the root to `sys.path`.

```bash
cd mycelium-core
python -m pytest -v
```

### Solidity compiler download fails during test
`test_compile_contract` triggers a real compilation. Ensure internet access on first run. Subsequent runs use cached solc binary.

---

## File System

### "chain-data files are locked" on Reset
Windows may hold file locks for 1-2 seconds after Geth stops. The application retries up to 8 times with progressive backoff. If all retries fail, manually kill `geth.exe` in Task Manager and delete `data/chain-data/active/`.

### Disk space growing over time
Chain-data is cleaned on each startup, but archived sessions accumulate in `data/logs/archive/`. Use **Reset Data** with the "Also delete archived session logs" checkbox to clean up.