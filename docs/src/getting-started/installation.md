# Installation

This guide walks through installing **MYCELIUM CORE** on a clean
Windows 10/11 machine. Linux and macOS are experimentally supported.

---

## System requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS         | Windows 10 64-bit            | Windows 11 64-bit |
| Python     | 3.11                         | 3.11.x latest patch |
| RAM        | 4 GB                         | 8 GB |
| Disk space | 500 MB free                  | 2 GB free |
| Network    | none required (fully local)  | — |

---

## Step 1. Clone the repository

```bash
git clone <repository-url> mycelium-core
cd mycelium-core
```

---

## Step 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

=== "Windows"

    ```bash
    venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    source venv/bin/activate
    ```

---

## Step 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

Expected packages: `PyQt6`, `web3`, `eth-account`, `py-solc-x`,
`qrcode`, `Pillow`, `qtawesome`, `python-dotenv`.

---

## Step 4. Place the Geth binary

Download [go-ethereum](https://geth.ethereum.org/downloads/) for your OS
and place the binary inside the project's `bin/` folder:

```text
bin/
├── geth.exe         # Windows
└── geth             # Linux / macOS
```

The application looks for the Geth binary **only inside `bin/`** and
does not depend on a system-wide installation.

---

## Step 5. Configure the environment

Copy the example configuration:

```bash
cp .env.example .env
```

Minimal `.env`:

```text
RPC_HOST=127.0.0.1
RPC_PORT=8545
DEV_MODE=true
DEV_ADMIN_KEY=0x...
```

The `DEV_ADMIN_KEY` is a convenience for testing — the application
will pre-fill the Admin key field. **Never use this in production-like
scenarios.**

To generate a test private key without running the full application:

```bash
python -c "from src.utils.crypto import generate_eth_keypair; \
           k,a = generate_eth_keypair(); \
           print('Key:', k); print('Address:', a)"
```

---

## Step 6. Verify the installation

```bash
python main.py
```

On first run the application:

1. Starts a local Geth node from `bin/`.
2. Waits up to 30 seconds for the RPC port to become ready.
3. Creates a new voting session.
4. Opens the main window.

If the main window appears with status **CONNECTED** in the footer,
the installation is successful.

---

## Troubleshooting

### Port 8545 is already in use

The application tries to terminate stale `geth.exe` processes on
startup. If the port is still busy, run:

```bash
taskkill /F /IM geth.exe /T
```

Then restart the application.

### "Geth not found" error

Verify the binary exists at `bin/geth.exe` (Windows) or `bin/geth`
(Linux/macOS) and has execute permissions.

### Solidity compiler download fails

`py-solc-x` downloads the Solidity compiler on first run. Ensure
internet access during the first deploy attempt. Subsequent runs use
the cached version.

---

## Next step

Continue with the [First Run](first-run.md) guide.