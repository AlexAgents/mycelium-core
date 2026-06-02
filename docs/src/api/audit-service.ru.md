# Модуль: AuditService

Аудит выборов на основе событий блокчейна. Читает события независимо
от состояния контракта для проверки инвариантов безопасности.

- **Файл:** `src/core/audit_service.py`
- **Класс:** `AuditService`

---

## Публичный API

### `run_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Полный аудит — все проверки.

### `run_pre_vote_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Предголосовые проверки: количество кандидатов, whitelist, стадия.

### `run_live_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Проверки во время голосования: двойное голосование, whitelist.

### `run_final_audit(session_id: str, deploy_block: int = 0) -> AuditReport`
Финальные проверки: все вышеперечисленные + валидация кандидатов, стадий, целостность
подсчёта, действия владельца.

---

## Результаты

### `build_results() -> list[Candidate]`
Вернет кандидатов, отсортированных по голосам по убыванию.

### `detect_winner() -> Optional[dict]`
Вернет `{"type": "winner", "candidate": Candidate}`, `{"type": "tie", "candidates": [...]}`, или
`None`.

---

## Проверки безопасности

| Метод | SEC | Что проверяет |
|---|---|---|
| `_check_double_vote` | SEC-01 | Нет дубликатов VoteCast.voter |
| `_check_whitelist_enforcement` | SEC-02 | Каждый голосовавший в whitelist |
| `_check_stage_enforcement` | SEC-03 | Все голоса в диапазоне блоков [start, end] |
| `_check_candidate_validation` | SEC-04 | Каждый кандидат в голосе зарегистрирован |
| `_check_owner_actions` | SEC-05 | Все admin-транзакции от owner |
| `_check_vote_count_integrity` | SEC-06 | Количество событий = сумма голосов |
| `_check_candidate_count` | Pre-vote | Зарегистрировано >= 2 кандидатов |
| `_check_whitelist_populated` | Pre-vote | Whitelist не пуст |