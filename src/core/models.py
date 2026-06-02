"""
Доменные модели данных MYCELIUM CORE.
Используются как DTO между слоями. Не содержат Web3-логики.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List, Optional


class ElectionStage(IntEnum):
    """Зеркалит enum Stage из смарт-контракта."""
    SETUP = 0
    ACTIVE = 1
    FINISHED = 2

    def display_name(self) -> str:
        return {
            ElectionStage.SETUP: "SETUP",
            ElectionStage.ACTIVE: "ACTIVE",
            ElectionStage.FINISHED: "FINISHED",
        }[self]


@dataclass
class Candidate:
    """Кандидат на выборах."""
    name: str
    party: str
    address: str
    vote_count: int = 0
    registered: bool = False

    def __post_init__(self) -> None:
        self.address = self.address.strip()
        self.name = self.name.strip()
        self.party = self.party.strip()


@dataclass
class Voter:
    """Избиратель в whitelist."""
    address: str
    private_key: Optional[str] = None
    has_voted: bool = False

    def __post_init__(self) -> None:
        self.address = self.address.strip()

    def to_export_dict(self) -> dict:
        d: dict = {"address": self.address, "has_voted": self.has_voted}
        if self.private_key is not None:
            d["private_key"] = self.private_key
        return d


@dataclass
class Election:
    """Конфигурация выборов."""
    title: str
    session_id: str
    max_candidates: int
    stage: ElectionStage = ElectionStage.SETUP
    start_block: int = 0
    end_block: int = 0
    total_votes: int = 0
    total_voters: int = 0

    @property
    def turnout_percent(self) -> float:
        if self.total_voters == 0:
            return 0.0
        return round(self.total_votes / self.total_voters * 100, 2)


@dataclass
class VoteReceipt:
    """Квитанция об успешном голосовании."""
    tx_hash: str
    voter_address: str
    candidate_address: str
    block_number: int
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    qr_bytes: Optional[bytes] = None

    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "voter_address": self.voter_address,
            "candidate_address": self.candidate_address,
            "block_number": self.block_number,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AuditCheck:
    """Результат одной проверки аудита."""
    check_name: str
    status: str  # "PASSED" | "FAILED" | "WARNING" | "SKIPPED"
    details: str


@dataclass
class AuditReport:
    """Полный отчёт аудита сессии."""
    session_id: str
    audit_timestamp: datetime
    checks: List[AuditCheck] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.status == "PASSED" for c in self.checks)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "PASSED")

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAILED")

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "audit_timestamp": self.audit_timestamp.isoformat(),
            "checks": [
                {
                    "check_name": c.check_name,
                    "status": c.status,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


@dataclass
class SessionContext:
    """
    Контекст активной сессии голосования.
    Сбрасывается при переходе к новой сессии.
    """
    session_id: Optional[str] = None
    contract_address: Optional[str] = None
    election: Optional[Election] = None
    candidates: List[Candidate] = field(default_factory=list)
    voters: List[Voter] = field(default_factory=list)
    abi: Optional[list] = None
    deploy_block: int = 0
    created_at: Optional[datetime] = field(default_factory=datetime.utcnow)

    def reset(self) -> None:
        """Очищает контекст для новой сессии."""
        self.session_id = None
        self.contract_address = None
        self.election = None
        self.candidates.clear()
        self.voters.clear()
        self.abi = None
        self.deploy_block = 0
        # FIX: было None — теперь корректно фиксируем время создания сессии
        self.created_at = datetime.utcnow()

    @property
    def is_deployed(self) -> bool:
        return self.contract_address is not None

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def voter_count(self) -> int:
        return len(self.voters)


@dataclass
class SecurityAuditSummary:
    total_checks: int
    passed: int
    failed: int
    warnings: int
    timestamp: datetime