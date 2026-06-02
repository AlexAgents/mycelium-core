# Руководство для контрибьюторов

Правила участия в разработке **MYCELIUM CORE**.

---

## Начало работы

1. Клонируйте репозиторий и настройте среду
   (см. [Настройка IDE](./setup.md)).

2. Создайте feature-ветку от `main`.
3. Внесите изменения.
4. Запустите все тесты: `python -m pytest -v`.
5. Отправьте pull request.

---

## Именование веток

| Тип | Паттерн | Пример |
|---|---|---|
| Фича | `feature/<краткое-описание>` | `feature/csv-export` |
| Баг-фикс | `fix/<краткое-описание>` | `fix/nonce-sync-error` |
| Документация | `docs/<краткое-описание>` | `docs/api-reference` |
| Рефакторинг | `refactor/<краткое-описание>` | `refactor/split-controller` |

---

## Формат коммит-сообщений

Следуйте спецификации
[Conventional Commits](https://www.conventionalcommits.org/):

```text
<тип>(<область>): <краткое описание>

<опциональное тело>

<опциональный футер>
```

### Типы

| Тип | Когда использовать |
|---|---|
| `feat` | Новая функциональность |
| `fix` | Исправление бага |
| `docs` | Только документация |
| `refactor` | Реструктуризация без изменения поведения |
| `test` | Добавление или обновление тестов |
| `chore` | Скрипты сборки, CI, инструменты |
| `style` | Форматирование, QSS, без изменения логики |

### Примеры

```text
feat(audit): add SEC-06 vote count integrity check

fix(geth): prevent false crash callback on intentional shutdown

docs(api): document all AppController public methods

test(nonce): add thread safety test with 4 concurrent threads
```

---

## Шаблон Pull Request

При создании PR используйте этот шаблон в описании:

```markdown
## Краткое описание

Что делает этот PR.

## Изменения

- [ ] Изменение 1
- [ ] Изменение 2

## Тип

- [ ] Фича
- [ ] Баг-фикс
- [ ] Документация
- [ ] Рефакторинг
- [ ] Тест

## Чек-лист

- [ ] Код соответствует [Руководству по стилю](./style-guide.md)
- [ ] Все существующие тесты проходят (`python -m pytest -v`)
- [ ] Добавлены новые тесты для новой функциональности
- [ ] Нет импортов `web3` / `eth_account` в `src/ui/`
- [ ] Все пользовательские строки используют i18n-ключи (не хардкод)
- [ ] Обновлены `ru.json` и `en.json` при добавлении новых ключей
- [ ] Docstrings добавлены для всех новых публичных методов
- [ ] Нет приватных ключей или секретов в логах или комментариях

## Связанные Issues

Closes #___
```

---

## Правила Code Review

### Чек-лист ревьюера

- [ ] Изменения соответствуют описанию PR.
- [ ] Изоляция слоёв сохранена (UI не импортирует `web3`).
- [ ] Новые публичные методы имеют аннотации типов и docstrings.
- [ ] Обработка ошибок следует проектным соглашениям (`RuntimeError`
  для бизнес-ошибок, конкретные исключения где возможно).

- [ ] Нет хардкод-строк на английском в UI — всё через `t()`.
- [ ] Тесты покрывают основной успешный путь и минимум один путь ошибки.
- [ ] Нет `except Exception: pass` в production-путях.

### Политика мержа

- Все тесты должны проходить.
- Требуется минимум одно одобрение.
- Предпочтителен squash merge для чистой истории.

---

## Архитектурные ограничения

Перед добавлением новых функций ознакомьтесь с:

- [ADR-006 (Слоистая архитектура)](../architecture/decisions/adr-006-layered-architecture.md) —
  UI ↔ AppController ↔ Services ↔ Infrastructure.

- [ADR-007 (Выделение ErrorParser)](../architecture/decisions/adr-007-error-parser-separation.md) —
  `AppController` должен оставаться компактным.

- [Руководство по стилю](./style-guide.md) — именование, импорты, обработка ошибок.

---

## Добавление нового воркера

При добавлении новой фоновой операции:

1. Создайте файл `src/ui/workers/<имя>_worker.py`.
2. Наследуйтесь от `BaseWorker`.
3. Реализуйте метод `run()` — эмитьте сигналы `progress`, `percent`,
   `finished` или `error`.

4. В UI-вкладке создайте воркер, подключите сигналы и запустите через
   `thread_runner.start_worker(worker)`.

5. Очистите чувствительные данные (приватные ключи) в блоке `finally`.

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