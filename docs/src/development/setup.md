# Development Setup

This page describes the recommended development environment for MYCELIUM CORE.

The project is a desktop research sandbox built with Python, PyQt6, Web3.py,
local Geth and Solidity smart contracts.

---

## Recommended Environment

| Component | Recommendation |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11+ |
| IDE | PyCharm or VS Code |
| Terminal | PowerShell or Windows Terminal |
| Blockchain node | Local Geth in `bin/` |
| Documentation | MkDocs Material |
| Tests | pytest |

---

## Структура репозитория
Проект разделён на две основные части:
```text
diploma-mycelium-core/
├── docs/                       # Документация MkDocs
└── mycelium-core/              # Приложение на Python
```

Исходный код приложения:
```text
mycelium-core/
├── main.py                     # Точка входа
├── bin/                        # Бинарник Geth
├── contracts/                  # Смарт-контракт Solidity
├── data/                       # Данные времени выполнения (gitignored)
├── scripts/                    # Скрипты сборки и очистки
├── src/
│   ├── core/                   # Бизнес-логика
│   ├── ui/                     # Интерфейс PyQt6
│   └── utils/                  # Утилиты
└── tests/                      # Набор тестов Pytest
```

Исходники документации:
```text
docs/
├── mkdocs.yml                  # Конфигурация MkDocs
├── requirements-docs.txt       # Зависимости для документации
├── generate_diagrams.py        # Компилятор PlantUML
├── plantuml.jar                # Бинарник PlantUML
└── src/                        # Исходные файлы Markdown
    └── diagrams/sources/       # Исходники .puml и .bpmn
```

---

## Python Environment

From the application root:

```bash
cd mycelium-core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Environment Configuration

Create `.env` from `.env.example` if available.

Minimal development configuration:

```text
RPC_HOST=127.0.0.1
RPC_PORT=8545
DEV_MODE=true
SOLIDITY_VERSION=0.8.20
```

Optional development admin key:

```text
DEV_ADMIN_KEY=0x...
```

!!! warning
    Development keys must not be real production keys.

---

## Geth Binary

Place Geth in:

```text
mycelium-core/bin/geth.exe
```

The application starts the local node from this path.

---

## Solidity Compiler

MYCELIUM CORE uses `py-solc-x`.

To install the required compiler manually:

```bash
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

---

## Run Application

```bash
python main.py
```

---

## Run Tests

```bash
python -m pytest -v
```

Integration tests:

```bash
python -m pytest -m integration -v
```

---

## Run Documentation

From the documentation root:

```bash
cd docs
pip install -r requirements-docs.txt
mkdocs serve
```

---

## Recommended IDE Settings

### Python Interpreter

Use the virtual environment created in the application root:

```text
mycelium-core/venv/
```

### Working Directory

For application runs:

```text
mycelium-core/
```

For documentation runs:

```text
docs/
```

---

## Development Notes

- UI code must not import Web3 directly.
- Blockchain write operations must go through services.
- Long-running UI operations must use workers.
- Private keys must not be logged.
- Documentation changes should be checked with `mkdocs build --strict`.