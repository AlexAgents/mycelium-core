"""
VoterStatus — DTO статуса избирателя для отображения в UI.

Используется AppController.get_voter_status() и UI VoteTab.
Не содержит Web3-логики, не зависит от Qt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VoterStatus:
    """
    Снимок статуса избирателя на момент запроса.

    Все поля Optional, потому что любой запрос к контракту
    может не выполниться (нет контракта, RPC недоступен и т.д.).
    UI должен корректно обрабатывать None.
    """
    key_valid: bool
    address: str = ""
    is_whitelisted: Optional[bool] = None
    has_voted: Optional[bool] = None
    balance_eth: Optional[str] = None
    stage_name: Optional[str] = None
    error: Optional[str] = None