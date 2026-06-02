# Contributing Guide

Guidelines for contributing to **MYCELIUM CORE**.

---

## Getting Started

1. Clone the repository and set up the environment
   (see [IDE Setup](./setup.md)).

2. Create a feature branch from `main`.
3. Make your changes.
4. Run all tests: `python -m pytest -v`.
5. Submit a pull request.

---

## Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feature/<short-description>` | `feature/csv-export` |
| Bug fix | `fix/<short-description>` | `fix/nonce-sync-error` |
| Documentation | `docs/<short-description>` | `docs/api-reference` |
| Refactor | `refactor/<short-description>` | `refactor/split-controller` |

---

## Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification:

```text
<type>(<scope>): <short description>

<optional body>

<optional footer>
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Build scripts, CI, tooling |
| `style` | Formatting, QSS changes, no logic change |

### Examples

```text
feat(audit): add SEC-06 vote count integrity check

fix(geth): prevent false crash callback on intentional shutdown

docs(api): document all AppController public methods

test(nonce): add thread safety test with 4 concurrent threads
```

---

## Pull Request Template

When opening a PR, use this template in the description:

```markdown
## Summary

Brief description of what this PR does.

## Changes

- [ ] Change 1
- [ ] Change 2

## Type

- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactor
- [ ] Test

## Checklist

- [ ] Code follows the [Style Guide](./style-guide.md)
- [ ] All existing tests pass (`python -m pytest -v`)
- [ ] New tests added for new functionality
- [ ] No `web3` / `eth_account` imports in `src/ui/`
- [ ] All user-facing strings use i18n keys (not hardcoded)
- [ ] Both `ru.json` and `en.json` updated if new keys added
- [ ] Docstrings added for all new public methods
- [ ] No private keys or secrets in logs or comments

## Related Issues

Closes #___
```

---

## Code Review Rules

### Reviewer Checklist

- [ ] Changes match the PR description.
- [ ] Layer isolation preserved (UI does not import `web3`).
- [ ] New public methods have type hints and docstrings.
- [ ] Error handling follows project conventions (`RuntimeError` for
  business errors, specific exceptions where possible).

- [ ] No hardcoded English strings in UI code — all go through `t()`.
- [ ] Tests cover the main success path and at least one failure path.
- [ ] No `except Exception: pass` in production paths.

### Merge Policy

- All tests must pass.
- At least one approval required.
- Squash merge preferred for clean history.

---

## Architecture Constraints

Before adding new features, review:

- [ADR-006 (Layered Architecture)](../architecture/decisions/adr-006-layered-architecture.md) —
  UI ↔ AppController ↔ Services ↔ Infrastructure.

- [ADR-007 (ErrorParser Separation)](../architecture/decisions/adr-007-error-parser-separation.md) —
  keep `AppController` thin.

- [Style Guide](./style-guide.md) — naming, imports, error handling.

---

## Adding a New Worker

When adding a new background operation:

1. Create a new file `src/ui/workers/<name>_worker.py`.
2. Subclass `BaseWorker`.
3. Implement `run()` method — emit `progress`, `percent`, `finished`,
   or `error` signals.

4. In the UI tab, create the worker, connect signals, and start via
   `thread_runner.start_worker(worker)`.

5. Clear any sensitive data (private keys) in the `finally` block.

```python
class MyWorker(BaseWorker):
    def __init__(self, controller, some_param):
        super().__init__()
        self.controller = controller
        self._param = some_param

    def run(self):
        try:
            self.percent.emit(30)
            result = self.controller.do_something(self._param)
            self.percent.emit(100)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
```