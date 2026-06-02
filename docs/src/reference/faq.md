# Frequently Asked Questions

Answers to common questions about setup, usage, and architecture of **MYCELIUM CORE**.

---

### Why do blocks start from 0 after every restart?

Geth `--dev` mode creates an ephemeral chain — state is stored in RAM,
only block headers are written to disk. This is an **architectural
decision** (see [ADR-003](../architecture/decisions/adr-003-ephemeral-chain.md)),
not a bug. One session = one voting.

---

### Why is the admin balance 0 after deploying the contract?

In dev mode, only the **Geth dev account** has funds — not your admin
private key. Click **Fund from Dev** (the hand-with-dollar icon next to
the balance field) to transfer 100 ETH from the dev account to your admin
address.

---

### What should I do if port 8545 is busy?

The application attempts to kill stale `geth.exe` processes on startup.
If the port is still occupied, run:

```bash
taskkill /F /IM geth.exe /T
```

Then restart the application. If the issue persists, change `RPC_PORT`
in `.env` to a free port (e.g. `8546`).

---

### Where are logs from previous sessions stored?

In `data/logs/archive/<session_id>/session.log`. Logs are automatically
archived when you create a new session or restart the application.

---

### Can this be used in a real production election?

**No.** MYCELIUM CORE is a **research sandbox** for a Master's thesis
project. Real elections require hardware signatures, cryptographic
anonymity, independent certification, and more. See
[Known Limitations](../security/known-limitations.md).

---

### Why PyQt6 and not PySide6?

See [ADR-001](../architecture/decisions/adr-001-pyqt6-choice.md). PyQt6
was chosen for better compatibility with PyInstaller and `qtawesome` on
Windows.

---

### How do I run the tests?

```bash
cd mycelium-core
python -m pytest -v
```

All tests live in the `tests/` directory. For integration tests (requires
Geth binary):

```bash
python -m pytest -m integration -v
```

See the [Testing Guide](../development/testing.md) for details.

---

### Does the Solidity compiler download automatically?

Yes. `py-solc-x` downloads the required compiler binary on the first
deploy attempt. Make sure you have internet access for the first run.
Subsequent runs use the cached version.

---

### How do I switch the theme?

Click the **theme toggle button** (adjust icon) in the header. The
selection is saved to `app.cfg` and persists across restarts.

---

### How do I change the interface language?

Use the **EN/RU combo box** in the header. Most labels update instantly.
A few require an application restart for full translation — you will see
a toast notification about this.

---

### What is `_SecretFilter` in the logger?

A security filter that automatically redacts private keys and sensitive
strings from all log entries. Strings matching `0x[a-fA-F0-9]{64}` or
containing keywords like `private_key`, `mnemonic`, or `secret` are
replaced with `[REDACTED]`.

---

### How does Mass Vote work?

Mass Vote iterates over a voter list and runs a 5-level pre-check for
each voter (key validity, whitelist, has_voted, balance). Eligible voters
cast a randomly selected vote. Failed voters are skipped — processing
continues to the next voter. Results are shown as:
`Voted N, skipped M, failed K`.

---

### Why does the admin key field lock after deploy?

To prevent accidentally changing the contract owner mid-session. The
field unlocks when you start a **New Session**.

---

### What happens when I click "Reset Data (TEST)"?

A legacy test function from early development. The system stops Geth,
deletes `chain-data/active/`, optionally deletes archived logs, restarts
Geth, and creates a fresh session. See the
[Reset Blockchain sequence diagram](../diagrams/sequence/reset-blockchain.md).

---

### How do I export the audit results?

On the **Audit** tab, after running an audit, use:

- **Copy Report** — copies to clipboard as JSON.
- **JSON** — saves full report to a `.json` file.
- **CSV** — saves structured report to a `.csv` file (sections:
  `[Results]`, `[Winner]`, `[Audit]`).

All three use a single source of truth:
`AppController.build_full_report()`.

---

### Will real ETH be spent if I paste a real private key?

No. The application runs on a local Geth `--dev` node (network ID 1337)
which is completely isolated from Ethereum mainnet and all public
testnets. Transactions never leave your machine.

However, pasting a real private key into any desktop application is
a security risk — the key exists in process memory. Always use
generated test keys for testing. See
[Known Limitations](../security/known-limitations.md#9-real-ethereum-accounts-and-private-keys).