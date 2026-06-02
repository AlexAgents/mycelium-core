"""
FundFromDevWorker — асинхронный перевод ETH с dev-аккаунта на admin.

Не блокирует UI на время ожидания подтверждения TX.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class FundFromDevWorker(BaseWorker):
    """Перевод ETH с dev-аккаунта Geth на указанный адрес."""

    def __init__(
        self,
        controller,
        target_address: str,
        amount_eth: float = 100.0,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._target = target_address
        self._amount = amount_eth

    def run(self) -> None:
        try:
            self.progress.emit("Sending TX from dev account...")
            self.percent.emit(30)
            tx_hash = self.controller.fund_from_dev(
                self._target, amount_eth=self._amount
            )
            self.percent.emit(100)
            self.finished.emit(tx_hash)
        except Exception as exc:
            self.error.emit(str(exc))