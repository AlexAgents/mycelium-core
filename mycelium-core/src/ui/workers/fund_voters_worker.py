"""
FundVotersWorker — фоновое пополнение балансов избирателей.
Итерирует по списку адресов и переводит ETH от администратора.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class FundVotersWorker(BaseWorker):
    """
    Принимает список адресов избирателей и сумму в wei.
    Последовательно вызывает controller.fund_voter() для каждого.
    Ключ администратора очищается после завершения.
    """

    def __init__(
        self,
        controller,
        admin_key: str,
        voter_addresses: list[str],
        amount_wei: int,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._admin_key = admin_key
        self._addresses = list(voter_addresses)
        self._amount_wei = amount_wei

    def run(self) -> None:
        try:
            total = len(self._addresses)
            if total == 0:
                self.error.emit("No voters to fund.")
                return

            for idx, addr in enumerate(self._addresses, 1):
                short = f"{addr[:8]}…{addr[-4:]}"
                self.progress.emit(
                    f"Funding {short} ({idx}/{total})…"
                )
                self.controller.fund_voter(
                    self._admin_key, addr, self._amount_wei,
                )
                # Emit percent
                pct = int(idx / total * 100)
                self.percent.emit(pct)

            self.finished.emit(total)

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self._admin_key = ""