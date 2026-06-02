"""
StageWorker — фоновое переключение стадий голосования.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class StageWorker(BaseWorker):
    """
    Вызывает controller.start_voting() или controller.finish_voting()
    в фоновом потоке.
    """

    def __init__(
        self,
        controller,
        admin_key: str,
        action: str,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._admin_key = admin_key
        self.action = action

    def run(self) -> None:
        try:
            if self.action == "start":
                self.progress.emit("Starting voting…")
                self.percent.emit(30)
                tx_hash = self.controller.start_voting(self._admin_key)
            elif self.action == "finish":
                self.progress.emit("Finishing voting…")
                self.percent.emit(30)
                tx_hash = self.controller.finish_voting(self._admin_key)
            else:
                self.error.emit(
                    f"Unknown stage action: {self.action}"
                )
                return

            self.percent.emit(100)
            self.finished.emit({
                "action": self.action,
                "tx_hash": tx_hash,
            })

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self._admin_key = ""