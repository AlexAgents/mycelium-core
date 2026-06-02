# Техническое задание (SRS): Документационный пакет

**Версия:** 1.0

**Дата:** 2026-05-20

**Тип документа:** Software Requirements Specification для документационного пакета

**Связанный проект:** MYCELIUM CORE v1.0.0

**Базовый SRS проекта:** docs/reference/srs.md



---

# 1. Цель и назначение

## 1.1. Цель

Создать профессиональный, исчерпывающий и поддерживаемый пакет
документации проекта MYCELIUM CORE, обеспечивающий:

- Быстрое погружение новых разработчиков (target: первая сборка ≤ 30 минут)
- Архитектурное понимание системы (диаграммы всех ключевых процессов)
- Аудиторскую прозрачность (сопоставление требований SRS и реализации)
- Поддержку проекта на длительный срок (≥ 5 лет)
- Возможность использования как учебного материала

## 1.2. Целевая аудитория документации

| Роль | Что должен найти |
|---|---|
| **Конечный пользователь** | Установка, первый запуск, инструкции по вкладкам |
| **Разработчик / контрибьютор** | Архитектура, API, гайд по разработке, тесты |
| **Системный аналитик** | UML диаграммы, BPMN процессы, модели данных |
| **Аудитор безопасности** | Threat model, SEC-проверки, audit procedure |
| **Технический менеджер** | Решения (ADR), changelog, метрики |
| **Студент / исследователь** | Полный референс blockchain-голосования |

## 1.3. Принципы документации

1. **Двуязычность** — все ключевые материалы на русском и английском
2. **Визуализация важнее текста** — каждый сложный процесс имеет диаграмму
3. **Каждая диаграмма имеет ноту** — пояснение "почему именно так"
4. **Single Source of Truth** — одна сущность описана в одном месте
5. **Версионирование** — документация имеет git-историю и changelog
6. **Локальный просмотр** — статический сайт через MkDocs
7. **Принцип "5 секунд"** — любой важный артефакт за 1-2 клика
8. **Diagram-as-code** — диаграммы хранятся как текстовые исходники
9. **Доступность** — соблюдение WCAG 2.1 AA где возможно

## 1.4. Метрики качества

| Метрика | Целевое значение |
|---|---|
| Покрытие требований SRS | ≥ 95% (каждое FR-*, NFR-* упомянуто) |
| Покрытие модулей `src/core/` API Reference | 100% |
| Покрытие модулей `src/ui/` user guide | ≥ 80% |
| Время первой сборки проекта по docs | ≤ 30 минут |
| Битые внутренние ссылки | 0 |
| Языковое соответствие RU↔EN | 100% ключей |

---

# 2. Технологический стек документации

## 2.1. Основной стек

| Компонент | Версия | Назначение |
|---|---|---|
| **MkDocs Material** | ≥ 9.5 | Статический генератор сайта |
| **mkdocs-static-i18n** | ≥ 1.2 | Многоязычность |
| **mkdocs-mermaid2-plugin** | ≥ 1.1 | Inline Mermaid диаграммы |
| **mkdocs-glightbox** | ≥ 0.3 | Lightbox для изображений |
| **mkdocstrings[python]** | ≥ 0.24 | Автогенерация API из docstrings |
| **PlantUML** | ≥ 1.2024 | Генерация UML диаграмм |
| **Camunda Modeler** или **bpmn.io** | latest | Создание BPMN диаграмм |
| **Figma** (опционально) | web | UI mockups |
| **Java Runtime** | ≥ 11 | Требуется для PlantUML.jar |

## 2.2. Файл зависимостей `docs/requirements-docs.txt`

```
mkdocs>=1.6.0
mkdocs-material>=9.5.0
mkdocs-static-i18n>=1.2.0
mkdocs-mermaid2-plugin>=1.1.0
mkdocs-glightbox>=0.3.0
mkdocstrings[python]>=0.24.0
pymdown-extensions>=10.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
```

## 2.3. Поддерживаемые форматы диаграмм

| Тип | Формат исходника | Формат экспорта | Инструмент |
|---|---|---|---|
| Component (UML) | `.puml` | `.svg` | PlantUML |
| Class (UML) | `.puml` | `.svg` | PlantUML |
| Sequence (UML) | `.puml` | `.svg` | PlantUML |
| State (UML) | `.puml` | `.svg` | PlantUML |
| Activity (UML) | `.puml` | `.svg` | PlantUML |
| Use Case (UML) | `.puml` | `.svg` | PlantUML |
| Deployment (UML) | `.puml` | `.svg` | PlantUML |
| C4 Architecture | `.puml` + C4 macros | `.svg` | PlantUML |
| Inline (простые) | Mermaid в .md | автоматический рендер | mkdocs-mermaid2-plugin |
| BPMN Business Process | `.bpmn` (XML) | `.svg` | bpmn.io / Camunda |
| UI Mockups | Figma project | `.png` | Figma |
| Screenshots | — | `.png` | OS screenshot tool |

---

# 3. Файловая структура документации

## 3.1. Целевая структура `docs/`

```
docs/
├── mkdocs.yml                  # Конфигурация MkDocs
├── requirements-docs.txt       # Зависимости Python
├── scripts/                    # Скрипт генерации/проверки UML
├── plantuml.jar                # Бинарник PlantUML
│
└── src/                        # Исходники MkDocs
    ├── index.md                # Главная страница
    ├── getting-started/        # Установка и запуск
    ├── user-guide/             # Руководство по вкладкам
    ├── architecture/           # Архитектура и ADR
    ├── api/                    # Code API
    ├── ui-design/              # UI Design
    ├── deployment/             # Деплой и сборка
    ├── security/               # Безопасность / модель угроз и аудит
    ├── development/            # Гайды контрибьюторов
    ├── reference/              # SRS, Changelog, FAQ
    │
    └── diagrams/               # Каталог диаграмм
        ├── index.md
        ├── architecture/       # Рендеры SVG
        ├── sequence/
        ├── state/
        ├── activity/
        ├── usecase/
        ├── bpmn/
        │
        └── sources/            # ИСХОДНИКИ диаграмм
            ├── uml/            # .puml (PlantUML)
            └── bpmn/           # .bpmn (Camunda/BPMN.io)
```

## 3.2. Принцип хранения диаграмм

| Файл | Под git | Источник | Назначение |
|---|---|---|---|
| `*.puml` | Да | Human-written | Исходник UML диаграммы |
| `*.bpmn` | Да | bpmn.io / Camunda | Исходник BPMN |
| `*.svg` (auto) | Да | `generate_diagrams.py` | Рендер для отображения |
| `*.png` (auto) | Да | `generate_diagrams.py` | Fallback для GitHub preview |
| `*.fig` (Figma) | Нет | Figma cloud | Хранится в Figma project |
| `*.png` (Figma export) | Да | Ручной экспорт | Используется в Markdown |

---

# 4. Содержание разделов документации

## 4.1. Главная страница (`index.md`)

**Назначение:** первая точка входа в документацию.

**Содержание:**

- Краткое описание проекта (1-2 абзаца)
- Скриншот главного окна
- Бейджи: версия, лицензия, статус тестов, языки
- 4 крупные ссылки-кнопки:
  - "Начать работу" → `getting-started/installation`
  - "Архитектура" → `architecture/overview`
  - "Документация API" → `api/`
  - "Безопасность" → `security/threat-model`
- Переключатель языка (предоставляется MkDocs Material)
- Поиск (предоставляется MkDocs Material)

## 4.2. Getting Started

### 4.2.1. `installation.md`

- Системные требования (OS, Python ≥ 3.11, RAM, диск)
- Установка Python и pip
- Установка зависимостей
- Размещение Geth binary
- Настройка `.env` файла
- Проверка установки
- Troubleshooting наиболее частых ошибок

### 4.2.2. `first-run.md`

- Запуск приложения
- Что происходит при старте (с скриншотами)
- Создание первого голосования за 5 минут
- Каждый шаг с скриншотом

### 4.2.3. `quick-tour.md`

- 5-минутный обзор всех 4 вкладок
- Аннотированные скриншоты с цифрами
- Ключевые функции каждой вкладки

## 4.3. User Guide

### 4.3.1. `overview.md`

- Концепция "одна сессия = одно голосование"
- Жизненный цикл голосования
- Роли пользователей

### 4.3.2. `admin-tab.md`
Полное описание Admin вкладки:

- Секция Contract: deploy, балансы, fund from dev
- Секция Candidates: добавление, регистрация
- Секция Voters: генерация, импорт, экспорт, whitelist, fund
- Секция Stage: start/finish voting
- Все диалоги (Confirm, Error, Toast)
- Скриншот вкладки с пронумерованными элементами

### 4.3.3. `vote-tab.md`

- Аутентификация избирателя
- Проверка статуса (whitelisted, has voted, balance)
- Выбор кандидата
- Mass Vote режим
- QR-квитанция

### 4.3.4. `audit-tab.md`

- 4 режима аудита (Full / Pre / Live / Final)
- Availability в зависимости от стадии
- Чтение результатов
- Copy Report / Export JSON / Export CSV
- Понимание SEC-проверок

### 4.3.5. `logs-tab.md`

- Просмотр логов сессии
- Поиск, автопрокрутка, информация о файле
- Сохранение, копирование

## 4.4. Architecture

### 4.4.1. `overview.md`

- Слоистая модель (схема)
- Обоснование выбранной архитектуры
- Ссылки на ADR
- **Должна содержать Component Diagram (PlantUML inline или ссылка)**

### 4.4.2. `layers.md`

- Детальное описание каждого слоя:
  - **UI Layer:** правила, ограничения, ответственность
  - **Application Layer (Controller):** фасадный паттерн
  - **Domain / Service Layer:** инкапсуляция бизнес-логики
  - **Infrastructure Layer:** Web3, Geth, Solidity
- Правила взаимодействия между слоями
- Список разрешённых и запрещённых паттернов

### 4.4.3. `components.md`

- Описание каждого компонента из Component Diagram
- Назначение, ответственность, зависимости
- Ссылки на API Reference

### 4.4.4. `data-flow.md`

- Поток данных при типовых операциях:
  - Голосование от UI до blockchain
  - Запуск аудита
  - Создание новой сессии
- **Sequence diagrams для каждого**

### 4.4.5. `decisions/` — ADR (Architecture Decision Records)

Каждый ADR следует стандартному шаблону:

# ADR-XXX: Заголовок решения

## Статус
Accepted | Superseded | Deprecated

## Дата
YYYY-MM-DD

## Контекст
Что было до решения, какая проблема возникла.

## Решение
Что было выбрано.

## Альтернативы

1. Альтернатива A — почему отклонена
2. Альтернатива B — почему отклонена

## Последствия

### Положительные

- ...

### Отрицательные

- ...

### Риски

- ...

## Связанные ADR

- ADR-XXX (related)

**Обязательные ADR (минимум 7):**

- ADR-001: PyQt6 vs PySide6
- ADR-002: Geth dev mode vs persistent chain
- ADR-003: Ephemeral chain между запусками
- ADR-004: Принцип "одна сессия = одно голосование"
- ADR-005: i18n с runtime switching
- ADR-006: Слоистая архитектура vs MVC/Clean
- ADR-007: ErrorParser отделён от AppController

## 4.5. Diagrams

### 4.5.1. `index.md`
Каталог всех диаграмм с миниатюрами и описаниями.
Группировка по типам.

### 4.5.2. Структура каждого `.md` файла диаграммы

# Название диаграммы

## Краткое описание
Одно-два предложения о назначении.

## Контекст
В рамках какого процесса используется эта диаграмма.

## Диаграмма

`![Diagram name] (../assets/diagrams/category/name.svg)`

## Нота / Объяснение
**Почему именно так:**

- Объяснение ключевых решений
- Объяснение выбранной нотации

## Связанные артефакты

- ADR: `[ADR-XXX] (../decisions/adr-xxx.md)`
- Код: `src/core/module.py`
- SRS: FR-XXX

## Источник
`diagrams/sources/uml/category/name.puml`

## История изменений
| Дата | Версия | Изменение |
|---|---|---|
| 2026-05-17 | 1.0 | Создана |

### 4.5.3. Обязательные диаграммы

**Architecture (UML Component, Class, Deployment, C4):**

| # | Имя | Тип | Назначение |
|---|---|---|---|
| 1 | component | UML Component | Все компоненты системы и связи |
| 2 | class | UML Class | Доменные модели (Election, Candidate, etc.) |
| 3 | deployment | UML Deployment | Физическое размещение (Python, Geth, Files) |
| 4 | c4-context | C4 Level 1 | Контекст системы |

**Sequence (UML Sequence):**

| # | Имя | Назначение |
|---|---|---|
| 5 | deploy-contract | Полный flow деплоя контракта |
| 6 | cast-vote | От клика "Cast Vote" до confirmation |
| 7 | mass-vote | Массовое голосование с pre-filtering |
| 8 | new-session | Создание новой сессии (быстрый режим) |
| 9 | reset-blockchain | Чистый режим (9 шагов) |
| 10 | geth-crash-recovery | Поведение при крэше Geth |

**State (UML State Machine):**

| # | Имя | Назначение |
|---|---|---|
| 11 | voting-lifecycle | SETUP → ACTIVE → FINISHED |
| 12 | session-states | NotStarted → InProgress → Archived |
| 13 | geth-states | Stopped → Starting → Running → Crashed |

**Activity (UML Activity):**

| # | Имя | Назначение |
|---|---|---|
| 14 | precheck-vote | 5 уровней проверки перед голосованием |
| 15 | geth-startup | Grace period + port check + retry |
| 16 | audit-process | Подготовка и выполнение аудита |

**Use Case (UML Use Case):**

| # | Имя | Назначение |
|---|---|---|
| 17 | system-use-cases | Все use cases для 3 актёров |

**BPMN 2.0 (бизнес-процессы):**

| # | Имя | Назначение |
|---|---|---|
| 18 | voting-business-process | Полный бизнес-процесс от подготовки до итогов |
| 19 | audit-workflow | Workflow аудитора |
| 20 | session-lifecycle | Бизнес-цикл сессии голосования |

**Итого минимум: 20 диаграмм**

## 4.6. API Reference

Структура для каждого модуля:

# Module: AppController

## Назначение
Высокоуровневый фасад между UI и сервисами.

## Расположение
`src/core/app_controller.py`

## Зависимости

- `VotingService`
- `AuditService`
- `CompilerService`
- ...

## Публичные методы

### `precheck_vote(voter_private_key: str) -> PrecheckResult`
**Назначение:** Полная pre-vote валидация.

**Параметры:**

- `voter_private_key` (str) — приватный ключ избирателя

**Возвращает:**

- `PrecheckResult` — структурированный результат

**Исключения:**

- `RuntimeError` — если нет активной сессии

**Пример:**

```python
result = controller.precheck_vote("0xabc...")
if result.is_ok:
    controller.cast_vote(...)
```

**Связанные:**

- `cast_vote()`, `precheck.py`

**Альтернатива:** автогенерация через `mkdocstrings` из docstrings кода.

Минимально документировать **все публичные методы** из:

- `AppController`
- `VotingService`
- `AuditService`
- `ErrorParser`
- `PrecheckResult / PrecheckStatus`
- `GethManager`
- `NonceManager`
- `Web3Provider`
- `CompilerService`

## 4.7. UI Design System

### 4.7.1. `design-system.md`

- Принципы дизайна
- Atomic Design структура

### 4.7.2. `color-palette.md`

- Полная палитра обеих тем
- Семантика каждого цвета
- Доступность (контраст WCAG 2.1)
- Hex / RGB значения

### 4.7.3. `typography.md`

- Используемые шрифты
- Иерархия размеров
- Веса

### 4.7.4. `components.md`

- Каталог всех UI-компонентов
- Состояния (default / hover / disabled / focus)
- Примеры использования
- Скриншоты

### 4.7.5. `icons.md`

- Все qtawesome иконки в проекте
- Семантика каждой
- Полный список для аудита

### 4.7.6. `figma-mockups.md`

- Ссылки на Figma project
- Экспортированные превью основных экранов
- Гайд по обновлению mockups

## 4.8. Deployment

### 4.8.1. `from-source.md`

- Установка для разработчика с нуля

### 4.8.2. `pyinstaller.md`

- Сборка standalone .exe
- Включение ресурсов (icons, themes, i18n)
- Подпись бинарника (опционально)
- Создание installer (опционально)

### 4.8.3. `distribution.md`

- Где публиковать релизы (GitHub Releases)
- Структура релиза
- Checksum проверка

### 4.8.4. `troubleshooting.md`
Полная сводка известных проблем и решений из обсуждений:

- Порт 8545 занят
- Geth не майнит блоки
- Файлы chain-data залочены
- Тесты не запускаются (sys.path)
- И т.д.

## 4.9. Security

### 4.9.1. `threat-model.md`

- STRIDE анализ
- Vectors of attack
- Mitigations
- Out-of-scope threats

### 4.9.2. `sec-checks.md`

- Детальное описание SEC-01..06
- Как реализованы в коде
- Как проверяются автоматически

### 4.9.3. `audit-procedure.md`

- Пошаговая процедура аудита нового релиза
- Checklist для аудитора
- Шаблон отчёта

### 4.9.4. `known-limitations.md`

- Эфемерная chain
- Single point of failure (Geth узел)
- Невозможность анонимного голосования
- Привязка к приватному ключу

## 4.10. Development

### 4.10.1. `setup.md`

- Setup IDE (VSCode / PyCharm)
- Рекомендуемые расширения
- Настройка форматтеров

### 4.10.2. `testing.md`

- Запуск pytest
- Структура тестов
- Покрытие
- Добавление новых тестов

### 4.10.3. `style-guide.md`

- PEP 8 + project conventions
- Naming
- Docstrings format
- Import order

### 4.10.4. `contributing.md`

- Branch workflow (Git Flow или GitHub Flow)
- Commit message format
- Pull request шаблон
- Code review правила

### 4.10.5. `git-workflow.md`

- Ветки (main, develop, feature/*, fix/*)
- Релизы (tags, releases)
- Hotfix процесс

## 4.11. Reference

### 4.11.1. `srs.md`
Копия оригинального SRS проекта (без изменений, для аудита).

### 4.11.2. `changelog.md`
Полный CHANGELOG в формате Keep a Changelog.

### 4.11.3. `glossary.md`
Терминологический словарь:

- Whitelist, Stage, Nonce, Genesis, ABI, Bytecode
- Smart Contract, Gas, Wei, ETH
- Pre-check, Audit, Session
- Все аббревиатуры (RPC, SRS, ADR, etc.)

### 4.11.4. `faq.md`
Расширенная версия FAQ из README + специфические вопросы для разработчиков.

### 4.11.5. `license.md`
Полный текст лицензии MIT.

---

# 5. Требования к диаграммам

## 5.1. Обязательные элементы каждой диаграммы

Каждая диаграмма должна содержать:

| Элемент | Описание |
|---|---|
| **Заголовок** | На обоих языках (EN основной, RU дублирующий) |
| **Версия** | Связь с версией проекта |
| **Дата создания** | YYYY-MM-DD |
| **Дата последнего обновления** | YYYY-MM-DD |
| **Автор** | ФИО или организация |
| **Легенда** | Расшифровка нотации (если нестандартная) |
| **Нота / Описание** | Объяснение "почему именно так" |
| **Связи** | Ссылки на ADR, sequence, code |

## 5.2. Стилистические требования

### 5.2.1. Цветовая семантика

| Цвет | Hex | Значение |
|---|---|---|
| Голубой | #388bfd | UI / Presentation layer |
| Зелёный | #3fb950 | Domain / Service layer |
| Жёлтый | #e3b341 | Infrastructure |
| Серый | #8b949e | External system |
| Красный | #f85149 | Critical / Security boundary |
| Фиолетовый | #a78bfa | Data / Storage |

### 5.2.2. Шрифты в диаграммах

- Sans-serif для всего текста
- Моноширинный (Consolas) для имён методов и кода
- Минимум 11pt для основного текста
- Минимум 9pt для подписей

### 5.2.3. Стрелки и связи

- UML стандарт по типам связей
- Solid arrow — синхронный вызов
- Dashed arrow — асинхронный / возврат
- Hollow triangle — наследование
- Diamond — композиция / агрегация

## 5.3. PlantUML — общая тема

В `src/diagrams/sources/uml/_common/theme.iuml` определяется единая тема:

```plantuml
@startuml
!define PRIMARY_COLOR #0969da
!define SUCCESS_COLOR #3fb950
!define WARNING_COLOR #e3b341
!define ERROR_COLOR #f85149
!define UI_COLOR #388bfd
!define DOMAIN_COLOR #3fb950
!define INFRA_COLOR #e3b341

skinparam backgroundColor white
skinparam defaultFontName Arial
skinparam defaultFontSize 12
skinparam shadowing false

skinparam component {
    BackgroundColor white
    BorderColor #444
    ArrowColor #555
}

skinparam class {
    BackgroundColor #f4f7fb
    BorderColor #c4d3e8
    ArrowColor #0969da
}

skinparam sequence {
    ArrowColor #0969da
    LifeLineBorderColor #c4d3e8
    LifeLineBackgroundColor #f4f7fb
    ParticipantBorderColor #444
}
@enduml
```

Все .puml файлы должны включать:
```plantuml
!include _common/theme.iuml
```

## 5.4. Скрипт генерации диаграмм

Файл `docs/generate_diagrams.py`:

**Функциональные требования:**

- Рекурсивно находит все `.puml` файлы в `src/diagrams/sources/uml/`
- Для каждого вызывает PlantUML jar для генерации SVG и PNG
- Размещает результаты в `docs/assets/diagrams/<category>/`
- Сохраняет структуру папок
- Логирует ошибки генерации
- Поддерживает флаг `--force` для регенерации
- Поддерживает флаг `--watch` для re-generate при изменениях

---

# 6. Требования к локализации документации

## 6.1. Языковой набор

- **Английский** — primary language, default
- **Русский** — вторичный, полное покрытие

## 6.2. Стандарт переводов

| Английский термин | Русский эквивалент |
|---|---|
| Voting | Голосование |
| Candidate | Кандидат |
| Voter | Избиратель |
| Whitelist | Whitelist (не переводится) |
| Smart contract | Смарт-контракт |
| Stage | Стадия |
| Session | Сессия |
| Audit | Аудит |
| Deploy | Деплой / Развёртывание |
| Nonce | Nonce (не переводится) |
| Gas | Газ |

## 6.3. Правила перевода

1. Технические термины (whitelist, nonce, RPC) **не переводятся**
2. Стандарты переводов для всех ключевых слов хранятся в `docs/glossary.md`
3. Каждая страница имеет 1:1 соответствие EN↔RU
4. При обновлении страницы обновляются обе версии
5. Имена файлов на английском, локализация через суффикс `.ru.md`

## 6.4. Покрытие локализацией

| Тип контента | Покрытие |
|---|---|
| Главная, Getting Started | 100% |
| User Guide | 100% |
| Architecture, Diagrams notes | 100% |
| ADR | 100% |
| API Reference | 50% (английский основной) |
| UI Design | 100% |
| Deployment, Security | 100% |
| Development | 50% (английский основной) |
| Reference | 100% |

---

# 7. Этапы реализации

## 7.1. Этап 1 — Базовая инфраструктура (1-2 дня)

**Результат:** Работающий MkDocs сайт с минимальным контентом.

**Задачи:**

- Создать структуру папок `docs/`
- Настроить `mkdocs.yml` (тема Material, i18n, плагины)
- Создать `requirements-docs.txt`
- Написать `generate_diagrams.py`
- Установить PlantUML.jar
- Создать `index.md` и `index.ru.md` (заглушки)
- Тестовый запуск `mkdocs serve`

**Критерий приёмки:**

- `mkdocs serve` запускается без ошибок
- Открывается http://127.0.0.1:8000
- Переключение тем работает
- Переключение языков работает (даже на пустых страницах)

## 7.2. Этап 2 — Перенос готового контента (1 день)

**Результат:** SRS, Changelog, Glossary доступны в документации.

**Задачи:**

- Перенести `srs.md` → `docs/docs/reference/srs.md`
- Перенести `changelog.md` → `docs/docs/reference/changelog.md`
- Создать `glossary.md`
- Создать `faq.md` на основе FAQ из README
- Создать `license.md`

**Критерий приёмки:**

- Все 5 файлов отображаются в навигации
- Markdown форматирование корректное
- Ссылки работают

## 7.3. Этап 3 — Архитектурные диаграммы (3-4 дня)

**Результат:** 4 базовые UML диаграммы в формате PlantUML.

**Задачи:**

- Создать общую тему `_common/theme.iuml`
- Component Diagram (.puml + описание в .md)
- Class Diagram (.puml + описание в .md)
- Deployment Diagram (.puml + описание в .md)
- C4 Context Diagram (.puml + описание в .md)
- Запуск `generate_diagrams.py` и проверка SVG

**Критерий приёмки:**

- 4 SVG файла в `docs/assets/diagrams/architecture/`
- 4 страницы описания в `docs/docs/diagrams/architecture/`
- Каждая страница имеет ноту с пояснением
- Диаграммы используют единую цветовую схему

## 7.4. Этап 4 — Sequence и State диаграммы (3-4 дня)

**Результат:** Все ключевые процессы визуализированы.

**Задачи:**

- 6 Sequence diagrams
- 3 State diagrams
- Описания для каждой
- Ссылки на соответствующий код и ADR

**Критерий приёмки:**

- 9 SVG файлов
- 9 страниц описаний
- Связь с FR-* идентификаторами SRS показана

## 7.5. Этап 5 — Activity и Use Case (1-2 дня)

**Результат:** Активности и use cases описаны.

**Задачи:**

- 3 Activity diagrams
- 1 Use Case diagram (все актёры)
- Описания

**Критерий приёмки:**

- 4 SVG файла + описания

## 7.6. Этап 6 — BPMN диаграммы (2 дня)

**Результат:** Бизнес-процессы описаны в BPMN 2.0.

**Задачи:**

- Создать 3 BPMN файла в Camunda Modeler или bpmn.io
- Voting Business Process (с пулами Администратор / Избиратель / Аудитор / Система)
- Audit Workflow
- Session Lifecycle
- Экспорт в SVG (ручной)
- Описания в Markdown

**Критерий приёмки:**

- 3 .bpmn файла в git
- 3 SVG в assets
- 3 страницы описаний

## 7.7. Этап 7 — Architecture pages (2 дня)

**Результат:** Полное описание архитектуры.

**Задачи:**

- `overview.md` — с inline диаграммами
- `layers.md` — детальные описания слоёв
- `components.md` — каталог компонентов
- `data-flow.md` — потоки данных
- 7 ADR (по нашим решениям из обсуждения)

**Критерий приёмки:**

- 4 страницы + 7 ADR
- Каждая страница ссылается на минимум 1 диаграмму
- Каждый ADR следует шаблону

## 7.8. Этап 8 — User Guide (2-3 дня)

**Результат:** Пользовательские инструкции с скриншотами.

**Задачи:**

- Сделать 10+ скриншотов всех вкладок в обеих темах
- `overview.md` — концепция приложения
- 4 файла по вкладкам с аннотированными скриншотами
- Сценарии использования

**Критерий приёмки:**

- 5 страниц User Guide
- Минимум 10 скриншотов
- Шаги пронумерованы и связаны со скриншотами

## 7.9. Этап 9 — API Reference (1-2 дня)

**Результат:** Документация публичных API.

**Задачи:**

- Настроить mkdocstrings
- Описать 9 ключевых модулей
- Добавить примеры использования

**Критерий приёмки:**

- 9 страниц API
- Все публичные методы AppController покрыты

## 7.10. Этап 10 — Security & Deployment (2 дня)

**Результат:** Документация безопасности и сборки.

**Задачи:**

- threat-model.md (STRIDE)
- sec-checks.md (детали SEC-01..06)
- audit-procedure.md
- known-limitations.md
- from-source.md
- pyinstaller.md
- distribution.md
- troubleshooting.md (расширенный из обсуждений)

**Критерий приёмки:**

- 8 страниц
- troubleshooting содержит ≥ 15 решённых проблем

## 7.11. Этап 11 — UI Design System (2 дня)

**Результат:** Документация дизайн-системы.

**Задачи:**

- design-system.md
- color-palette.md с примерами цветов
- typography.md
- components.md с превью
- icons.md полный список qtawesome
- figma-mockups.md (если есть Figma)

**Критерий приёмки:**

- 6 страниц
- Все используемые иконки задокументированы

## 7.12. Этап 12 — Development guide (1-2 дня)

**Результат:** Гайд для контрибьюторов.

**Задачи:**

- setup.md
- testing.md
- style-guide.md
- contributing.md
- git-workflow.md

**Критерий приёмки:**

- 5 страниц
- contributing.md содержит PR template

## 7.13. Этап 13 — Полная локализация на русский (4-5 дней)

**Результат:** Вся документация двуязычна.

**Задачи:**

- Перевести все 70+ страниц на русский
- Обновить glossary
- Проверить корректность ссылок
- Проверить рендеринг на обоих языках

**Критерий приёмки:**

- 100% соответствие EN↔RU
- Все внутренние ссылки работают
- Переключатель языка работает на каждой странице

## 7.14. Этап 14 — Финальная проверка и публикация (1-2 дня)

**Результат:** Production-ready документационный сайт.

**Задачи:**

- Прогон linter для markdown
- Проверка всех ссылок (markdown-link-check)
- Проверка отображения в браузере (Chrome, Firefox, Safari)
- Тест на мобильном
- Опционально: настройка GitHub Actions для автодеплоя
- Опционально: деплой на GitHub Pages

**Критерий приёмки:**

- 0 битых ссылок
- Сайт открывается на всех браузерах
- Время загрузки ≤ 2 сек на средней скорости

---

# 8. Сводные критерии приёмки

Документационный пакет считается готовым, если выполнены **все** условия:

## 8.1. Инфраструктура

1. `mkdocs serve` запускается без ошибок и предупреждений
2. Сайт доступен по `http://127.0.0.1:8000`
3. Поиск работает на обоих языках
4. Темы dark/light переключаются
5. Языки EN/RU переключаются
6. Все плагины MkDocs работают корректно

## 8.2. Содержание

7. Минимум 70 страниц контента (без учёта переводов)
8. Все 20 обязательных диаграмм созданы
9. Минимум 7 ADR в формате Markdown
10. SRS, Changelog, Glossary, FAQ присутствуют
11. API Reference покрывает 100% публичных методов core-модулей

## 8.3. Диаграммы

12. Все PlantUML файлы рендерятся в SVG без ошибок
13. BPMN файлы корректно открываются в bpmn.io
14. Каждая диаграмма имеет ноту с пояснением
15. Цветовая схема диаграмм единообразна
16. Используется единая тема PlantUML

## 8.4. Локализация

17. 100% страниц имеют русскую версию (кроме API Reference)
18. Glossary содержит ≥ 30 терминов с переводами
19. Переключатель языка работает на всех страницах
20. Ссылки между языковыми версиями консистентны

## 8.5. Качество

21. 0 битых внутренних ссылок (проверено markdown-link-check)
22. Все скриншоты в актуальной версии (не из бета-версий проекта)
23. Markdown файлы соответствуют project style (если есть линтер)
24. Все примеры кода корректные и запускаются
25. Дата последнего обновления указана на каждой странице

## 8.6. Соответствие SRS проекта

26. Все FR-* идентификаторы из SRS упомянуты хотя бы в одном месте
27. Все NFR-* блоки имеют соответствующие разделы в docs
28. Все 23 приёмочных критерия SRS отражены в документации

---

# 9. Ограничения и допущения

## 9.1. Ограничения

- Документация не заменяет код-комментарии — это разные уровни
- Не все детали реализации описываются (только архитектурно важные)

## 9.2. Допущения

- Пользователь имеет базовое знание Markdown
- Для просмотра документации требуется Python и MkDocs (или браузер для статического сайта)
- BPMN диаграммы создаются вручную через GUI инструменты
- Figma mockups опциональны и могут быть добавлены позже

---

# 10. Контактная информация

**Ответственный за документацию:** Alex
**Owner проекта:** Alex
**Дата создания SRS документации:** 2024-05-17

---

## Статус реализации

Документационный пакет, описанный в данном ТЗ, полностью реализован
в составе **MYCELIUM CORE v1.0.1**.

### Поставленные артефакты

1. **Настройка MkDocs** — `mkdocs.yml`, `requirements-docs.txt`,
   `scripts/build_docs.py`, `scripts/generate_diagrams.py`.
2. **PlantUML диаграммы** — 17 диаграмм в 5 категориях
   (Architecture, Sequence, State, Activity, Use Case).
3. **BPMN 2.0 процессы** — 6 бизнес-процессов с XML-исходниками
   для Camunda Modeler.
4. **ADR записи** — 7 Architecture Decision Records (ADR-001–007).
5. **API Reference** — 10 основных модулей, документированных на EN
   и RU.
6. **Глоссарий, FAQ, SRS, Changelog** — все справочные страницы
   реализованы.
7. **Полная русская локализация** — соответствие EN↔RU по всем
   разделам.

### Расположение

```text
docs/src/reference/srs-docs.ru.md  ← Это ТЗ
```