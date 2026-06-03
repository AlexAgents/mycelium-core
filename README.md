<div align="center">

<img src="mycelium-core/src/assets/icons/Original.png"
     alt="MYCELIUM CORE Logo" width="120">

# MYCELIUM CORE

> Настольное sandbox-приложение для моделирования, проведения и аудита
> электронного голосования на локальной Ethereum-сети.
> Симулятор для Master Degree Project.

[![Release](https://img.shields.io/github/v/release/AlexAgents/mycelium-core?color=blue&label=)](https://github.com/AlexAgents/mycelium-core/releases) [![License](https://img.shields.io/github/license/AlexAgents/mycelium-core?color=yellow&label=)](LICENSE) [![Python](https://img.shields.io/badge/Python%203.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/) [![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/) [![Solidity](https://img.shields.io/badge/Solidity%200.8.20-363636?logo=solidity&logoColor=white)](https://docs.soliditylang.org/en/v0.8.20/) [![Tests](https://img.shields.io/badge/Tests-180%20passed-success)](https://github.com/AlexAgents/mycelium-core/tree/main/mycelium-core/tests) [![MkDocs](https://img.shields.io/badge/MkDocs-0969da?logo=materialformkdocs&logoColor=white)](https://github.com/AlexAgents/mycelium-core/tree/main/docs) [![Figma](https://img.shields.io/badge/Figma-Mockups-F24E1E?logo=figma&logoColor=white)](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)

[![README English](https://img.shields.io/badge/README-English-2ea44f?logo=readme&logoColor=white)](README.en.md) &nbsp; [![README Русский](https://img.shields.io/badge/README-Русский-0969da?logo=readme&logoColor=white)](README.md)

**[Артефакты](#артефакты)** · **[Архитектура](#архитектура)** · **[Дизайн](#дизайн)** · **[Скриншоты](#скриншоты)** · **[Быстрый старт](#быстрый-старт)** · **[Конфигурация](#конфигурация)** · **[Безопасность](#инварианты-безопасности)** · **[FAQ](docs/src/reference/faq.ru.md)**

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

## Артефакты

<table>
<tr>
<th nowrap>Категория</th>
<th nowrap>Артефакт</th>
<th nowrap>Кол-во</th>
<th>Ссылка</th>
</tr>
<tr>
<td nowrap>Документация</td>
<td>Сайт MkDocs (EN/RU)</td>
<td nowrap>70+ стр.</td>
<td><a href="docs/src/index.ru.md">Открыть</a></td>
</tr>
<tr>
<td nowrap>UML-диаграммы</td>
<td>Component, Class, Sequence, State, Activity, UseCase, Deployment, C4</td>
<td nowrap>17</td>
<td><a href="docs/src/diagrams/index.ru.md">Каталог</a></td>
</tr>
<tr>
<td nowrap>Процессы BPMN</td>
<td>Setup, Voting, Mass Vote, Audit, Error Handling, Session Lifecycle</td>
<td nowrap>6</td>
<td><a href="docs/src/diagrams/index.ru.md">Каталог</a></td>
</tr>
<tr>
<td nowrap>ADR</td>
<td>ADR-001 -- ADR-007</td>
<td nowrap>7</td>
<td><a href="docs/src/architecture/overview.ru.md">Обзор</a></td>
</tr>
<tr>
<td nowrap>Безопасность</td>
<td>STRIDE модель угроз + SEC-01..06</td>
<td nowrap>7</td>
<td><a href="docs/src/security/threat-model.ru.md">Угрозы</a></td>
</tr>
<tr>
<td nowrap>API Reference</td>
<td>Спецификации модулей ядра</td>
<td nowrap>10</td>
<td><a href="docs/src/api/index.ru.md">API</a></td>
</tr>
<tr>
<td nowrap>UI-макеты</td>
<td>Figma-файл с аннотациями</td>
<td nowrap>53 ноты</td>
<td><a href="https://www.figma.com/design/XXXXXXXXX/mycelium-core">Figma</a></td>
</tr>
<tr>
<td nowrap>Дизайн-система</td>
<td>Цвета, шрифты, компоненты</td>
<td nowrap>6 стр.</td>
<td><a href="docs/src/ui-design/design-system.ru.md">Дизайн</a></td>
</tr>
<tr>
<td nowrap>SRS</td>
<td>Проект + Документация</td>
<td nowrap>2</td>
<td><a href="docs/src/reference/srs.ru.md">SRS</a></td>
</tr>
<tr>
<td nowrap>Тесты</td>
<td>Unit + Integration (реальный Geth)</td>
<td nowrap>180</td>
<td><a href="docs/src/development/testing.ru.md">Тесты</a></td>
</tr>
<tr>
<td nowrap>Глоссарий</td>
<td>Термины и аббревиатуры</td>
<td nowrap>33</td>
<td><a href="docs/src/reference/glossary.ru.md">Глоссарий</a></td>
</tr>
<tr>
<td nowrap>FAQ</td>
<td>Частые вопросы</td>
<td nowrap>16</td>
<td><a href="docs/src/reference/faq.ru.md">FAQ</a></td>
</tr>
</table>

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
<img src="docs/src/assets/images/screenshots/admin-tab-dark.png"
     alt="Admin Tab Dark" width="480">
</td>
<td align="center">
<img src="docs/src/assets/images/screenshots/admin-tab-light.png"
     alt="Admin Tab Light" width="480">
</td>
</tr>
</table>

</details>

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
<img src="docs/src/assets/images/screenshots/vote-tab-dark.png"
     alt="Vote Tab Dark" width="480">
</td>
<td align="center">
<img src="docs/src/assets/images/screenshots/vote-tab-light.png"
     alt="Vote Tab Light" width="480">
</td>
</tr>
</table>

</details>

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
<img src="docs/src/assets/images/screenshots/audit-tab-dark.png"
     alt="Audit Tab Dark" width="480">
</td>
<td align="center">
<img src="docs/src/assets/images/screenshots/audit-tab-light.png"
     alt="Audit Tab Light" width="480">
</td>
</tr>
</table>

</details>

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
<img src="docs/src/assets/images/screenshots/logs-tab-dark.png"
     alt="Logs Tab Dark" width="480">
</td>
<td align="center">
<img src="docs/src/assets/images/screenshots/logs-tab-light.png"
     alt="Logs Tab Light" width="480">
</td>
</tr>
</table>

</details>

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
<img src="docs/src/assets/images/screenshots/about-dialog.png"
     alt="About Dialog" width="480">
</td>
<td align="center">
<img src="docs/src/assets/images/screenshots/reset-blockchain-dialog.png"
     alt="Reset Blockchain Dialog" width="480">
</td>
</tr>
</table>

</details>

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

## Конфигурация

Все параметры времени выполнения настраиваются через `.env`.
Скопируйте `.env.example` в `.env` и измените нужные значения.

### Режимы Geth

Приложение запускает Geth только в режиме `--dev`. Это архитектурное
решение (см. [ADR-002](docs/src/architecture/decisions/adr-002-geth-dev-mode.ru.md)).

<table>
<tr>
<th nowrap>Параметр</th>
<th nowrap>По умолчанию</th>
<th>Описание</th>
</tr>
<tr>
<td nowrap><code>RPC_HOST</code></td>
<td nowrap><code>127.0.0.1</code></td>
<td nowrap>Хост JSON-RPC Geth</td>
</tr>
<tr>
<td nowrap><code>RPC_PORT</code></td>
<td nowrap><code>8545</code></td>
<td nowrap>Порт JSON-RPC Geth</td>
</tr>
<tr>
<td nowrap><code>GETH_NETWORK_ID</code></td>
<td nowrap><code>1337</code></td>
<td nowrap>ID локальной сети</td>
</tr>
</table>

### Параметры транзакций

<table>
<tr>
<th nowrap>Параметр</th>
<th nowrap>По умолчанию</th>
<th>Описание</th>
</tr>
<tr>
<td nowrap><code>DEFAULT_GAS</code></td>
<td nowrap><code>500000</code></td>
<td nowrap>Лимит газа на транзакцию</td>
</tr>
<tr>
<td nowrap><code>DEFAULT_GAS_PRICE</code></td>
<td nowrap><code>1000000000</code></td>
<td nowrap>Цена газа в Wei (1 Gwei)</td>
</tr>
</table>

### Параметры UI — время и таймауты

Захардкожены в коде — при необходимости менять в исходниках:

<table>
<tr>
<th nowrap>Константа</th>
<th nowrap>Файл</th>
<th nowrap>Значение</th>
<th>Описание</th>
</tr>
<tr>
<td nowrap><code>_TOAST_DURATION_MS</code></td>
<td nowrap><code>toast.py</code></td>
<td nowrap><code>2500</code></td>
<td nowrap>Время показа тоста (мс)</td>
</tr>
<tr>
<td nowrap><code>_TOAST_GAP_MS</code></td>
<td nowrap><code>toast.py</code></td>
<td nowrap><code>150</code></td>
<td nowrap>Пауза между тостами (мс)</td>
</tr>
<tr>
<td nowrap><code>--dev.period</code></td>
<td nowrap><code>geth_manager.py</code></td>
<td nowrap><code>5</code></td>
<td nowrap>Интервал блоков (сек)</td>
</tr>
<tr>
<td nowrap><code>RPC_WAIT_TIMEOUT_SEC</code></td>
<td nowrap><code>web3_provider.py</code></td>
<td nowrap><code>30</code></td>
<td nowrap>Таймаут RPC (сек)</td>
</tr>
<tr>
<td nowrap><code>timeout</code></td>
<td nowrap><code>voting_service.py</code></td>
<td nowrap><code>120</code></td>
<td nowrap>Таймаут TX (сек)</td>
</tr>
</table>

### Dev-режим

<table>
<tr>
<th nowrap>Параметр</th>
<th nowrap>По умолчанию</th>
<th>Описание</th>
</tr>
<tr>
<td nowrap><code>DEV_MODE</code></td>
<td nowrap><code>true</code></td>
<td nowrap>Включает dev-удобства</td>
</tr>
<tr>
<td nowrap><code>DEV_ADMIN_KEY</code></td>
<td nowrap><em>(пусто)</em></td>
<td nowrap>Автозаполнение admin key</td>
</tr>
<tr>
<td nowrap><code>LOG_LEVEL</code></td>
<td nowrap><code>INFO</code></td>
<td nowrap>DEBUG / INFO / WARNING</td>
</tr>
<tr>
<td nowrap><code>SOLIDITY_VERSION</code></td>
<td nowrap><code>0.8.20</code></td>
<td nowrap>Версия компилятора Solidity</td>
</tr>
</table>

## Инварианты безопасности

Критические бизнес-правила обеспечиваются проактивно на уровне
смарт-контракта и верифицируются реактивно через `AuditService`:

<table>
<tr>
<th nowrap>Код</th>
<th nowrap>Проверка</th>
<th nowrap>Контракт</th>
<th nowrap>Аудит</th>
</tr>
<tr>
<td nowrap>SEC-01</td>
<td nowrap>Двойной голос</td>
<td nowrap><code>hasVoted[sender]</code></td>
<td nowrap>Нет дублей событий</td>
</tr>
<tr>
<td nowrap>SEC-02</td>
<td nowrap>Whitelist</td>
<td nowrap><code>require(whitelist[sender])</code></td>
<td nowrap>Все в whitelist</td>
</tr>
<tr>
<td nowrap>SEC-03</td>
<td nowrap>Стадия</td>
<td nowrap><code>onlyStage(Active)</code></td>
<td nowrap>Голоса в диапазоне блоков</td>
</tr>
<tr>
<td nowrap>SEC-04</td>
<td nowrap>Кандидаты</td>
<td nowrap><code>require(candidates[c].registered)</code></td>
<td nowrap>Только зарегистрированным</td>
</tr>
<tr>
<td nowrap>SEC-05</td>
<td nowrap>Admin</td>
<td nowrap>модификатор <code>onlyOwner</code></td>
<td nowrap>TX от владельца</td>
</tr>
<tr>
<td nowrap>SEC-06</td>
<td nowrap>Целостность</td>
<td nowrap>неявно <code>votes += 1</code></td>
<td nowrap>Событий = сумма голосов</td>
</tr>
</table>

## Лицензия

Распространяется под лицензией **MIT**. Подробнее — в файле
[LICENSE](LICENSE).

**Автор:** AlexAgents