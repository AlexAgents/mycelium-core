# Style Guide

This page defines coding and documentation conventions for MYCELIUM CORE.

The goal is not to enforce excessive bureaucracy, but to keep the project
readable, testable and maintainable.

---

## General Principles

1. Keep UI and business logic separated.
2. Keep blockchain logic out of Qt widgets.
3. Prefer small focused services over large mixed classes.
4. Prefer typed DTOs over unstructured dictionaries.
5. Do not log secrets.
6. Keep documentation aligned with the implemented version.

---

## Python Code Style

### Formatting

Use standard Python formatting conventions:

- 4 spaces for indentation;
- descriptive names;
- type hints for public methods;
- small functions where possible.

---

## Imports

Recommended order:

```python
from __future__ import annotations

import os
import json
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from src.core.models import Candidate
from src.utils.logger import get_logger
```

Groups:

1. future imports;
2. standard library;
3. third-party libraries;
4. local project imports.

---

## UI Layer Rules

Files under:

```text
src/ui/
```

must not import:

- `web3`;
- `eth_account`;
- `solcx`.

UI should:

- render widgets;
- collect input;
- show messages;
- start workers;
- call `AppController`.

UI should not:

- build blockchain transactions;
- sign transactions;
- call smart contract functions directly;
- implement contract rules.

---

## Core Layer Rules

Files under:

```text
src/core/
```

contain application and domain logic.

Allowed responsibilities:

- session coordination;
- blockchain service methods;
- audit checks;
- error parsing;
- nonce management;
- compiler orchestration;
- Geth lifecycle.

Core code should avoid direct UI imports.

---

## Worker Rules

Workers should be thin wrappers around controller calls.

Worker responsibilities:

- run long operation in background thread;
- emit progress;
- emit result;
- emit error;
- clear sensitive local references where applicable.

Workers should not duplicate business rules already implemented in services.

---

## Logging Rules

Never log:

- private keys;
- seed phrases;
- mnemonic phrases;
- raw secrets;
- full sensitive JSON payloads.

Allowed:

- short addresses;
- transaction hashes;
- operation names;
- error summaries.

---

## i18n Rules

User-facing UI text should use translation keys.

English and Russian JSON dictionaries must contain the same keys.

Documentation pages should have EN/RU pairs where applicable:

```text
page.md
page.ru.md
```

---

## Documentation Style

Each technical page should answer:

1. What is this?
2. Why does it exist?
3. How does it work?
4. Where is the code?
5. What are the limitations?

---

## Diagram Page Style

Each diagram page should contain:

- purpose;
- context;
- diagram image;
- reading guide;
- relation to code;
- source link;
- known limitations.

---

## Security Language

Avoid claiming production-grade security.

Correct:

```text
research sandbox
demo security checks
audit-oriented validation
```

Avoid:

```text
production-ready election system
anonymous voting
government-grade security
```

---

## Commit and Review Notes

Before merging documentation changes:

```bash
cd docs
python scripts/audit_docs_symmetry.py
mkdocs build --strict
```

Before merging code changes:

```bash
cd mycelium-core
python -m pytest -v
```