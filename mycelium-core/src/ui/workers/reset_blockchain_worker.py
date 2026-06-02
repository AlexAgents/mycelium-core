"""
ResetBlockchainWorker — асинхронный сброс blockchain-данных.

Не блокирует UI на время остановки Geth, удаления файлов и перезапуска.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class ResetBlockchainWorker(BaseWorker):
    """Сброс chain-data + опционально архивов + перезапуск Geth."""

    def __init__(
        self,
        controller,
        delete_logs: bool = False,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._delete_logs = delete_logs

    def run(self) -> None:
        try:
            self.progress.emit("Stopping Geth...")
            self.percent.emit(15)

            self.progress.emit("Waiting for file locks to release...")
            self.percent.emit(35)

            self.progress.emit("Deleting blockchain data...")
            self.percent.emit(60)

            self.controller.reset_blockchain_data(
                delete_archived_logs=self._delete_logs,
            )

            self.progress.emit("Restarting Geth...")
            self.percent.emit(85)

            self.percent.emit(100)
            self.finished.emit(True)
        except Exception as exc:
            self.error.emit(str(exc))