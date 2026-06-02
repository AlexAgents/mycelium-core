"""
Запуск worker'ов в QThread.
"""
from __future__ import annotations

from PyQt6.QtCore import QThread


class ThreadRunner:
    def __init__(self) -> None:
        self._threads: list[QThread] = []

    # ─────────────────────────────────────────────────────────────
    def start_worker(self, worker) -> QThread:
        thread = QThread()
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(thread.quit)
        worker.error.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._cleanup_threads)

        self._threads.append(thread)
        thread.start()
        return thread

    # ─────────────────────────────────────────────────────────────
    def _cleanup_threads(self) -> None:
        """Удаляет из списка все завершённые потоки."""
        self._threads = [
            t for t in self._threads if not t.isFinished()
        ]

    # ─────────────────────────────────────────────────────────────
    def active_count(self) -> int:
        """Количество активных (незавершённых) потоков."""
        return sum(
            1 for t in self._threads if not t.isFinished()
        )