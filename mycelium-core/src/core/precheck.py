"""
Pre-vote checks — бизнес-логика проверки готовности к голосованию.

Используется AppController.precheck_vote().
UI получает структурированный результат и показывает понятное сообщение.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PrecheckStatus(Enum):
    """Результат предварительной проверки перед голосованием."""
    OK = "ok"
    INVALID_KEY = "invalid_key"
    NOT_WHITELISTED = "not_whitelisted"
    ALREADY_VOTED = "already_voted"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    NO_CONTRACT = "no_contract"
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class PrecheckResult:
    """Структура результата precheck."""
    status: PrecheckStatus
    address: str = ""
    balance_wei: int = 0
    required_wei: int = 0
    error_text: str = ""

    @property
    def is_ok(self) -> bool:
        return self.status == PrecheckStatus.OK