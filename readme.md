<div align="center">

<img src="mycelium-core/src/assets/icons/Original.png"
     alt="MYCELIUM CORE Logo" width="120">

# MYCELIUM CORE

> Настольное sandbox-приложение для моделирования, проведения и аудита
> электронного голосования на локальной Ethereum-сети.

![Version](https://img.shields.io/badge/version-1.0.1-blue)
[![License](https://img.shields.io/github/license/AlexAgents/mycelium-core?color=yellow)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-41CD52?logo=qt&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-0.8.20-363636?logo=solidity&logoColor=white)
![Tests](https://img.shields.io/badge/tests-180_passed-success)
![Docs](https://img.shields.io/badge/docs-MkDocs_Material-0969da?logo=materialformkdocs&logoColor=white)

[![RU](https://img.shields.io/badge/Language-RU-blue.svg)](README.md)
[![EN](https://img.shields.io/badge/Language-EN-blue.svg)](README.en.md)

**[Артефакты](#артефакты)** ·
**[Архитектура](#архитектура)** ·
**[Дизайн](#дизайн)** ·
**[Скриншоты](#скриншоты)** ·
**[Быстрый старт](#быстрый-старт)** ·
**[Конфигурация](#конфигурация)** ·
**[Безопасность](#инварианты-безопасности)** ·
**[FAQ](docs/src/reference/faq.ru.md)** ·
**[Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)**

</div>

---

## Обзор

MYCELIUM CORE — автономная desktop-среда для симуляции процесса
блокчейн-голосования. Система использует единственный Solidity
смарт-контракт (`VotingCore.sol`) как абсолютный источник истины,
эфемерный локальный узел Geth для исполнения и многослойный
графический интерфейс на PyQt6.

Проект демонстрирует полный жизненный цикл on-chain выборов:
подготовку, голосование и событийно-ориентированный криптографический
аудит.

---

## Артефакты

| Категория | Артефакт | Количество | Ссылка |
|:---|:---|:---|:---|
| Документация | Сайт MkDocs (EN/RU) | 70+ страниц | [Открыть](docs/src/index.ru.md) |
| UML-диаграммы | PlantUML (Component, Class, Sequence, State, Activity, Use Case, Deployment, C4) | 17 | [Каталог](docs/src/diagrams/index.ru.md) |
| Процессы BPMN | Camunda Modeler (Setup, Voting, Mass Vote, Audit, Error Handling, Session Lifecycle) | 6 | [Каталог](docs/src/diagrams/index.ru.md) |
| Архитектурные решения | ADR-001 -- ADR-007 | 7 | [Обзор](docs/src/architecture/overview.ru.md) |
| Безопасность | STRIDE модель угроз + SEC-01..06 | 1+6 | [Модель угроз](docs/src/security/threat-model.ru.md) |
| API Reference | Спецификации модулей ядра | 10 | [API](docs/src/api/index.ru.md) |
| UI-макеты | Figma-файл с 53 аннотационными нотами | 53 ноты | [Открыть в Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) |
| Дизайн-система | Палитра, типографика, компоненты | 6 страниц | [Дизайн-система](docs/src/ui-design/design-system.ru.md) |
| SRS | Основной + SRS документации | 2 | [SRS](docs/src/reference/srs.ru.md) |
| Тесты | Unit + Integration (реальный Geth) | 180 пройдено | [Тестирование](docs/src/development/testing.ru.md) |
| Глоссарий | Термины и аббревиатуры | 33 термина | [Глоссарий](docs/src/reference/glossary.ru.md) |
| FAQ | Частые вопросы | 16 вопросов | [FAQ](docs/src/reference/faq.ru.md) |

---

## Архитектура

Система реализует строгую слоистую архитектуру. Слою представления
(UI) запрещено импортировать Web3, Solidity или криптографические
библиотеки напрямую.

```text
┌─────────────────────────────────────┐
│  UI Layer (PyQt6 Widgets + Workers) │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  AppController (Facade)             │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  Services (Voting / Audit / Error)  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ Infrastructure (Web3 / Geth / Nonce)│
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  VotingCore.sol (Smart Contract)    │
└─────────────────────────────────────┘
```

---

## Дизайн

UI-макеты с полной системой аннотаций поддерживаются в Figma.

**[Открыть Figma-файл (только просмотр)](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)**

Файл содержит:
- 4 макета вкладок (Admin, Vote, Audit, Logs)
- 5 типов диалогов (Новая сессия, Массовое голосование, Финансирование, Выход, Сброс)
- Вариативные компоненты (StatusBadge, Toast, ProgressBar, LogBox)
- 53 аннотационные ноты с цветовой кодировкой по категориям
- Маркеры-пины, связывающие ноты с элементами интерфейса

Полная спецификация: [Дизайн-система](docs/src/ui-design/design-system.ru.md) |
[Цветовая палитра](docs/src/ui-design/color-palette.ru.md) |
[Структура Figma](docs/src/ui-design/figma-mockups.ru.md)

---

## Скриншоты

<details>
<summary>Вкладка Admin — деплой контракта, кандидаты, избиратели, управление стадией</summary>

<br>

<table>
<tr>
<th align="center">Тёмная тема</th>
<th align="center">Светлая тема</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/admin-tab-dark.png"
     alt="Admin Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/admin-tab-light.png"
     alt="Admin Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>Вкладка Голосование — аутентификация, выбор кандидата, QR-квитанция</summary>

<br>

<table>
<tr>
<th align="center">Тёмная тема</th>
<th align="center">Светлая тема</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/vote-tab-dark.png"
     alt="Vote Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/vote-tab-light.png"
     alt="Vote Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>Вкладка Аудит — SEC-проверки, результаты, экспорт</summary>

<br>

<table>
<tr>
<th align="center">Тёмная тема</th>
<th align="center">Светлая тема</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/audit-tab-dark.png"
     alt="Audit Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/audit-tab-light.png"
     alt="Audit Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>Вкладка Логи — лог сессии, живой поиск, автопрокрутка</summary>

<br>

<table>
<tr>
<th align="center">Тёмная тема</th>
<th align="center">Светлая тема</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/logs-tab-dark.png"
     alt="Logs Tab Dark" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/logs-tab-light.png"
     alt="Logs Tab Light" width="480">
</td>
</tr>
</table>

</details>

---

<details>
<summary>Диалоги — О программе, Сброс блокчейна</summary>

<br>

<table>
<tr>
<th align="center">О программе</th>
<th align="center">Сброс блокчейна</th>
</tr>
<tr>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/about-dialog.png"
     alt="About Dialog" width="480">
</td>
<td align="center">
<img src="mycelium-core/src/assets/images/screenshots/reset-blockchain-dialog.png"
     alt="Reset Blockchain Dialog" width="480">
</td>
</tr>
</table>

</details>

---

## Быстрый старт

### 1. Предварительные требования

- Python 3.11+
- Бинарник [Go-Ethereum (Geth)](https://geth.ethereum.org/downloads/),
  размещённый в `mycelium-core/bin/`
  (`bin/geth.exe` для Windows, `bin/geth` для Linux/macOS).

### 2. Установка

```bash
git clone https://github.com/AlexAgents/mycelium-core.git
cd mycelium-core/mycelium-core
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### 3. Запуск приложения

```bash
python main.py
```

### 4. Запуск документации (MkDocs)

Для локального рендера UML-диаграмм скачайте
[`plantuml.jar`](https://github.com/plantuml/plantuml/releases/) и
поместите его в папку `docs/`.

```bash
cd ../../docs
pip install -r requirements-docs.txt
mkdocs serve
# Открыть http://127.0.0.1:8000
```

---

## Конфигурация

Все параметры времени выполнения настраиваются через `.env`.
Скопируйте `.env.example` в `.env` и измените нужные значения.

### Режимы Geth

Приложение запускает Geth только в режиме `--dev`. Это архитектурное
решение (см. [ADR-002](docs/src/architecture/decisions/adr-002-geth-dev-mode.ru.md)).

| Параметр | По умолчанию | Описание |
|---|---|---|
| `RPC_HOST` | `127.0.0.1` | Хост JSON-RPC Geth |
| `RPC_PORT` | `8545` | Порт JSON-RPC Geth |
| `GETH_NETWORK_ID` | `1337` | ID локальной сети |

### Параметры транзакций

| Параметр | По умолчанию | Описание |
|---|---|---|
| `DEFAULT_GAS` | `500000` | Лимит газа на транзакцию |
| `DEFAULT_GAS_PRICE` | `1000000000` | Цена газа в Wei (1 Gwei) |

### Параметры UI — время и таймауты

Захардкожены в коде — при необходимости менять в исходниках:

| Константа | Файл | По умолчанию | Описание |
|---|---|---|---|
| `_TOAST_DURATION_MS` | `src/ui/widgets/toast.py` | `2500` | Время показа тоста (мс) |
| `_TOAST_GAP_MS` | `src/ui/widgets/toast.py` | `150` | Пауза между тостами (мс) |
| `--dev.period` | `src/core/geth_manager.py` | `5` | Интервал блоков Geth (сек) |
| `RPC_WAIT_TIMEOUT_SEC` | `src/core/web3_provider.py` | `30` | Таймаут подключения к RPC (сек) |
| `timeout` | `src/core/voting_service.py` | `120` | Таймаут подтверждения TX (сек) |

### Dev-режим

| Параметр | По умолчанию | Описание |
|---|---|---|
| `DEV_MODE` | `true` | Включает dev-удобства |
| `DEV_ADMIN_KEY` | *(пусто)* | Автозаполнение поля admin key при старте |
| `LOG_LEVEL` | `INFO` | Уровень логирования: DEBUG / INFO / WARNING |
| `SOLIDITY_VERSION` | `0.8.20` | Версия компилятора Solidity |

---

## Инварианты безопасности

Критические бизнес-правила обеспечиваются проактивно на уровне
смарт-контракта и верифицируются реактивно через `AuditService`:

| Код | Проверка | Защита в контракте | Верификация аудитом |
|---|---|---|---|
| SEC-01 | Двойное голосование | `hasVoted[msg.sender]` | Нет дублей в событиях `VoteCast` |
| SEC-02 | Whitelist | `require(whitelist[msg.sender])` | Все избиратели в whitelist |
| SEC-03 | Стадия | `onlyStage(Stage.Active)` | События в диапазоне `[start, end]` блоков |
| SEC-04 | Кандидаты | `require(candidates[c].registered)` | Голоса только зарегистрированным |
| SEC-05 | Действия admin | модификатор `onlyOwner` | Admin TX от владельца контракта |
| SEC-06 | Целостность | неявно `votes += 1` | Число событий = сумма голосов |

---

## Лицензия

Распространяется под лицензией **MIT**. Подробнее — в файле
[LICENSE](LICENSE).

**Автор:** AlexAgents