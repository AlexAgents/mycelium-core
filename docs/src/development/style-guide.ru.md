# Style Guide

Эта страница определяет соглашения по коду и документации MYCELIUM CORE.

Цель — не бюрократия, а читаемость, тестируемость и поддерживаемость проекта.

---

## Общие принципы

1. Разделять UI и business logic.
2. Не помещать blockchain logic в Qt widgets.
3. Предпочитать небольшие focused services крупным смешанным классам.
4. Предпочитать typed DTOs неструктурированным словарям.
5. Не логировать секреты.
6. Поддерживать документацию в соответствии с реализованной версией.

---

## Python code style

### Форматирование

Использовать стандартные Python conventions:

- 4 пробела для indentation;
- понятные имена;
- type hints для публичных методов;
- небольшие функции, где возможно.

---

## Imports

Рекомендуемый порядок:

```python
from __future__ import annotations

import os
import json
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from src.core.models import Candidate
from src.utils.logger import get_logger
```

Группы:

1. future imports;
2. standard library;
3. third-party libraries;
4. local project imports.

---

## Правила UI layer

Файлы в:

```text
src/ui/
```

не должны импортировать:

- `web3`;
- `eth_account`;
- `solcx`.

UI должен:

- отрисовывать widgets;
- собирать input;
- показывать messages;
- запускать workers;
- вызывать `AppController`.

UI не должен:

- строить blockchain transactions;
- подписывать transactions;
- напрямую вызывать smart contract functions;
- реализовывать contract rules.

---

## Правила core layer

Файлы в:

```text
src/core/
```

содержат application и domain logic.

Допустимые responsibilities:

- session coordination;
- blockchain service methods;
- audit checks;
- error parsing;
- nonce management;
- compiler orchestration;
- Geth lifecycle.

Core code не должен импортировать UI.

---

## Правила workers

Workers должны быть тонкими wrapper-объектами вокруг controller calls.

Responsibilities worker:

- выполнять длительную операцию в background thread;
- отправлять progress;
- отправлять result;
- отправлять error;
- очищать sensitive local references, где применимо.

Workers не должны дублировать business rules, уже реализованные в services.

---

## Правила логирования

Нельзя логировать:

- private keys;
- seed phrases;
- mnemonic phrases;
- raw secrets;
- полные sensitive JSON payloads.

Разрешено:

- короткие addresses;
- transaction hashes;
- operation names;
- краткие error summaries.

---

## Правила i18n

User-facing UI text должен использовать translation keys.

English и Russian JSON dictionaries должны содержать одинаковые keys.

Documentation pages должны иметь EN/RU пары, где применимо:

```text
page.md
page.ru.md
```

---

## Documentation style

Каждая техническая страница должна отвечать:

1. Что это?
2. Зачем это существует?
3. Как это работает?
4. Где код?
5. Какие ограничения?

---

## Diagram page style

Каждая страница диаграммы должна содержать:

- purpose;
- context;
- diagram image;
- reading guide;
- relation to code;
- source link;
- known limitations.

---

## Security language

Не нужно заявлять production-grade security.

Корректно:

```text
research sandbox
demo security checks
audit-oriented validation
```

Некорректно:

```text
production-ready election system
anonymous voting
government-grade security
```

---

## Commit and review notes

Перед merge изменений документации:

```bash
cd docs
python scripts/audit_docs_symmetry.py
mkdocs build --strict
```

Перед merge изменений кода:

```bash
cd mycelium-core
python -m pytest -v
```