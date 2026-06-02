# Building from Source

How to set up a development environment for **MYCELIUM CORE**.

---

## Prerequisites

- Python 3.11+
- Git
- Geth binary (see [Installation](../getting-started/installation.md))

---

## Clone and Install

```bash
git clone <repository-url> mycelium-core
cd mycelium-core
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

---

## Project Structure

```text
mycelium-core/
├── main.py                     # Entry point
├── app.cfg                     # User settings (auto-generated)
├── .env                        # Environment config (gitignored)
├── .env.example                # Environment template
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── readme.md                   # Project README
├── .gitignore                  # Git ignore rules
│
├── bin/                        # Binaries
│   └── geth.exe                # Local Geth node
│
├── contracts/                  # Smart contracts
│   └── VotingCore.sol          # Core contract
│
├── data/                       # Runtime data (gitignored)
│   ├── chain-data/             # Blockchain state
│   └── logs/                   # Session logs
│
├── scripts/                    # CI/CD and utilities
│   ├── builder.py              # EXE builder script
│   └── clean.*                 # Deep cleanup scripts (.bat, .ps1, .sh)
│
├── src/                        # Source code
│   ├── assets/                 # Static assets (icons)
│   ├── core/                   # Business logic and services
│   ├── ui/                     # PyQt6 interface
│   │   ├── i18n/               # Localization JSONs
│   │   ├── tabs/               # UI tabs
│   │   ├── themes/             # QSS styles
│   │   ├── widgets/            # Custom reusable widgets
│   │   └── workers/            # Async background threads (QThread)
│   └── utils/                  # Helpers (logger, config, paths, crypto)
│
└── tests/                      # Test suite
    ├── conftest.py             # Pytest fixtures
    └── test_*.py               # Unit and integration tests
```

---

## Run

```bash
python main.py
```

---

## Run Tests

```bash
python -m pytest -v
```

---

## IDE Recommendations

- **VSCode:** Install Python, Pylance, and Solidity extensions.
- **PyCharm:** Mark `src/` as Sources Root. Set pytest as test runner.

Both IDEs should use the project's virtual environment as the Python interpreter.