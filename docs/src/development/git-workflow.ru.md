# Git-процесс

Управление ветками и процесс релизов для **MYCELIUM CORE**.

---

## Модель веток

Проект использует упрощённый **GitHub Flow**:

```text
main ─────────────────────────────────────────►
  │                                    ▲
  ├── feature/csv-export ──────────────┤ (PR + squash merge)
  │                                    │
  ├── fix/nonce-sync ──────────────────┤
  │                                    │
  └── docs/api-reference ──────────────┘
```

### Ветки

| Ветка | Назначение | Время жизни |
|---|---|---|
| `main` | Стабильный, готовый к релизу код | Постоянная |
| `feature/*` | Новая функциональность | До мержа |
| `fix/*` | Исправления багов | До мержа |
| `docs/*` | Обновления документации | До мержа |
| `refactor/*` | Реструктуризация кода | До мержа |

---

## Шаги рабочего процесса

### 1. Создайте ветку

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### 2. Разрабатывайте и коммитьте

```bash
git add .
git commit -m "feat(scope): description"
```

Следуйте формату
[Conventional Commits](https://www.conventionalcommits.org/)
(см. [Руководство для контрибьюторов](./contributing.md)).

### 3. Отправьте и откройте PR

```bash
git push origin feature/my-feature
```

Откройте Pull Request на GitHub в ветку `main`.

### 4. Ревью и мерж

- Все тесты должны проходить.
- Требуется минимум одно одобрение.
- Используйте **Squash and merge** для чистой истории коммитов.

### 5. Очистка

После мержа удалите feature-ветку:

```bash
git checkout main
git pull origin main
git branch -d feature/my-feature
```

---

## Релизы

### Версионирование

Проект следует [Семантическому версионированию](https://semver.org/lang/ru/):

- **MAJOR** — breaking changes (изменение ABI контракта, несовместимый API).
- **MINOR** — новые функции, обратная совместимость.
- **PATCH** — исправления багов, обновления документации.

### Создание релиза

1. Обновите версию в `src/utils/config.py` (`APP_VERSION`).
2. Обновите версию в `src/ui/widgets/about_dialog.py` (`APP_VERSION`).
3. Обновите версию по умолчанию в `app.cfg`.
4. Обновите `Changelog` в `docs/src/reference/changelog.md`.
5. Коммит: `chore(release): bump version to X.Y.Z`.
6. Тег: `git tag vX.Y.Z`.
7. Отправка: `git push origin main --tags`.
8. Сборка EXE: `python scripts/builder.py --build`.
9. Создание GitHub Release с тегом, прикрепление EXE и checksums.

---

## Процесс хотфикса

Для критических исправлений выпущенной версии:

1. Создайте ветку от последнего тега:
   ```bash
   git checkout -b fix/critical-bug vX.Y.Z
   ```

2. Примените исправление, коммит, пуш.
3. Откройте PR в `main`.
4. После мержа создайте тег нового патча: `vX.Y.(Z+1)`.
5. Соберите и выпустите релиз.