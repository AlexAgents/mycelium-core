"""
WhitelistWorker — фоновое добавление избирателей в whitelist.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class WhitelistWorker(BaseWorker):
    """
    Вызывает controller.whitelist_voters() в фоновом потоке.
    Ключ администратора очищается после завершения.
    """

    def __init__(self, controller, admin_key: str) -> None:
        super().__init__()
        self.controller = controller
        self._admin_key = admin_key

    def run(self) -> None:
        try:
            self.progress.emit("Adding voters to whitelist…")
            self.percent.emit(30)

            tx_hash = self.controller.whitelist_voters(self._admin_key)
            count = len(self.controller.session.voters)

            self.percent.emit(100)
            self.finished.emit({
                "tx_hash": tx_hash,
                "count": count,
            })

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self._admin_key = ""