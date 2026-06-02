"""
StatusWorker — фоновый опрос состояния Ethereum-ноды
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.ui.workers.base_worker import BaseWorker


@dataclass
class StatusData:
    """DTO с данными о состоянии ноды, передаётся через сигнал finished."""
    connected: bool
    block: Optional[int]
    client: str
    contract: Optional[str]
    stage: Optional[str]


class StatusWorker(BaseWorker):
    """
    Собирает статус RPC, блока, клиента и стадии контракта в фоновом потоке.
    finished.emit(StatusData) → слот в MainWindow обновляет виджеты.
    """

    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

    def run(self) -> None:
        try:
            connected = self.controller.get_rpc_status()
            block = self.controller.get_block_number()
            contract = self.controller.session.contract_address

            stage: Optional[str] = None
            client: str = "unknown"

            if contract:
                try:
                    stage = self.controller.get_stage().name
                except Exception:
                    pass
                try:
                    client = self.controller.provider.client_version()
                except Exception:
                    pass

            self.finished.emit(StatusData(
                connected=connected,
                block=block,
                client=client,
                contract=contract,
                stage=stage,
            ))
        except Exception as exc:
            self.error.emit(str(exc))