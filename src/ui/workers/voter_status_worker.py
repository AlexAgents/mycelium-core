"""
VoterStatusWorker — асинхронная проверка whitelist/hasVoted.
Используется в VoteTab вместо синхронных RPC-вызовов при каждом нажатии клавиши.
"""
from __future__ import annotations

from dataclasses import dataclass

from eth_account import Account

from src.ui.workers.base_worker import BaseWorker


@dataclass
class VoterStatusData:
    """DTO с результатом проверки статуса избирателя."""
    address: str
    whitelisted: bool
    has_voted: bool


class VoterStatusWorker(BaseWorker):
    """
    Принимает приватный ключ, получает адрес, запрашивает whitelist и hasVoted.
    Ключ очищается сразу после использования (в блоке finally).
    """

    def __init__(self, controller, private_key: str) -> None:
        super().__init__()
        self.controller = controller
        self._private_key = private_key

    def run(self) -> None:
        try:
            account = Account.from_key(self._private_key)
            addr = account.address
            whitelisted = self.controller.is_whitelisted(addr)
            voted = self.controller.has_voted(addr)
            self.finished.emit(VoterStatusData(
                address=addr,
                whitelisted=whitelisted,
                has_voted=voted,
            ))
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            # FIX: очищаем ключ сразу после использования
            self._private_key = ""