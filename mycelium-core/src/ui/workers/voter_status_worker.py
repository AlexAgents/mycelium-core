"""
VoterStatusWorker — фоновый запрос статуса избирателя.

Не содержит бизнес-логики. Только вызывает controller.get_voter_status().
Возвращает (private_key_used, VoterStatus) — UI использует private_key_used
для проверки актуальности (мог уже смениться ключ в поле).
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class VoterStatusWorker(BaseWorker):
    """
    Получает снимок статуса избирателя в фоновом потоке.

    Сигналы:
        finished((str, VoterStatus)) — кортеж (ключ, статус).
            Ключ нужен UI чтобы проверить: статус ещё актуален или уже
            пользователь ввёл другой ключ.
        error(str) — критическая ошибка.
    """

    def __init__(self, controller, private_key: str) -> None:
        super().__init__()
        self.controller = controller
        self._private_key = private_key

    def run(self) -> None:
        try:
            status = self.controller.get_voter_status(
                self._private_key
            )
            self.finished.emit((self._private_key, status))
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self._private_key = ""