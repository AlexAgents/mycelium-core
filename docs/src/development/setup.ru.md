# Настройка среды разработки

Эта страница описывает рекомендуемую среду разработки для MYCELIUM CORE.

Проект является desktop research sandbox на Python, PyQt6, Web3.py, локальном
Geth и Solidity smart contract.

---

## Рекомендуемая среда

| Компонент | Рекомендация |
|---|---|
| ОС | Windows 10/11 |
| Python | 3.11+ |
| IDE | PyCharm или VS Code |
| Терминал | PowerShell или Windows Terminal |
| Blockchain node | Локальный Geth в `bin/` |
| Документация | MkDocs Material |
| Тесты | pytest |

---

## Структура репозитория

Проект разделён на две основные части:

```text
diploma-mycelium-core/
├── docs/
└── mycelium-core/
```

Исходный код приложения:

```text
mycelium-core/
├── main.py
├── contracts/
├── src/
├── tests/
└── scripts/
```

Исходники документации:

```text
docs/
├── mkdocs.yml
├── scripts/
└── src/
```

---

## Python environment

Из корня приложения:

```bash
cd mycelium-core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Конфигурация окружения

Создайте `.env` из `.env.example`, если пример доступен.

Минимальная development-конфигурация:

```text
RPC_HOST=127.0.0.1
RPC_PORT=8545
DEV_MODE=true
SOLIDITY_VERSION=0.8.20
```

Опциональный development admin key:

```text
DEV_ADMIN_KEY=0x...
```

!!! warning
    Development keys не должны быть реальными production-ключами.

---

## Geth binary

Поместите Geth в:

```text
mycelium-core/bin/geth.exe
```

Приложение запускает локальный узел из этого пути.

---

## Solidity Compiler

MYCELIUM CORE использует `py-solc-x`.

Ручная установка требуемого compiler:

```bash
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

---

## Запуск приложения

```bash
python main.py
```

---

## Запуск тестов

```bash
python -m pytest -v
```

Integration tests:

```bash
python -m pytest -m integration -v
```

---

## Запуск документации

Из корня документации:

```bash
cd docs
pip install -r requirements-docs.txt
mkdocs serve
```

---

## Рекомендуемые настройки IDE

### Python Interpreter

Используйте виртуальное окружение из корня приложения:

```text
mycelium-core/venv/
```

### Working Directory

Для запуска приложения:

```text
mycelium-core/
```

Для запуска документации:

```text
docs/
```

---

## Development notes

- UI code не должен напрямую импортировать Web3.
- Blockchain write operations должны проходить через services.
- Длительные UI operations должны выполняться через workers.
- Private keys не должны попадать в логи.
- Изменения документации нужно проверять через `mkdocs build --strict`.