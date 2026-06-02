"""
AuditService.
Полный event-based аудит голосования.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from web3 import Web3

from src.core.models import AuditCheck, AuditReport
from src.core.voting_service import VotingService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    def __init__(self, voting_service: VotingService) -> None:
        self.voting_service = voting_service

    # ─────────────────────────────────────────────────────────────
    def run_audit(
        self,
        session_id: str,
        deploy_block: int = 0,
    ) -> AuditReport:
        """
        Запускает все проверки безопасности.

        deploy_block — номер блока, в котором был задеплоен контракт
        (из SessionContext.deploy_block). Используется для ограничения
        диапазона поиска событий.
        """
        logger.info("Running security audit")
        checks: list[AuditCheck] = []
        vote_events = self._get_vote_events(deploy_block)

        checks.append(self._check_double_vote(vote_events))
        checks.append(self._check_whitelist_enforcement(vote_events))
        checks.append(self._check_candidate_validation(vote_events))
        # FIX: передаём deploy_block для реальной проверки блоков
        checks.append(self._check_stage_enforcement(vote_events, deploy_block))
        checks.append(self._check_vote_count_integrity(vote_events))

        report = AuditReport(
            session_id=session_id,
            audit_timestamp=datetime.utcnow(),
            checks=checks,
        )
        logger.info(
            "Audit finished passed=%s failed=%d",
            report.all_passed, report.failed_count,
        )
        return report

    # ─────────────────────────────────────────────────────────────
    # Results
    # ─────────────────────────────────────────────────────────────
    def build_results(self):
        candidates = self.voting_service.get_candidates()
        return sorted(candidates, key=lambda c: c.vote_count, reverse=True)

    def detect_winner(self):
        results = self.build_results()
        if not results:
            return None
        top = results[0]
        tied = [c for c in results if c.vote_count == top.vote_count]
        if len(tied) > 1:
            return {"type": "tie", "candidates": tied}
        return {"type": "winner", "candidate": top}

    # ─────────────────────────────────────────────────────────────
    # Event extraction
    # ─────────────────────────────────────────────────────────────
    def _get_vote_events(self, from_block: int = 0):
        contract = self.voting_service.contract
        if contract is None:
            raise RuntimeError("Contract not loaded")
        latest_block = self.voting_service.provider.w3.eth.block_number
        events = contract.events.VoteCast.get_logs(
            from_block=from_block,
            to_block=latest_block,
        )
        logger.info("Loaded %d VoteCast events", len(events))
        return events

    # ─────────────────────────────────────────────────────────────
    # Checks
    # ─────────────────────────────────────────────────────────────
    def _check_double_vote(self, vote_events) -> AuditCheck:
        voters = [e["args"]["voter"] for e in vote_events]
        duplicates = [
            addr for addr, count in Counter(voters).items() if count > 1
        ]
        if duplicates:
            return AuditCheck(
                check_name="Double Vote Protection",
                status="FAILED",
                details=f"Duplicate voters: {duplicates}",
            )
        return AuditCheck(
            check_name="Double Vote Protection",
            status="PASSED",
            details="No duplicate votes detected",
        )

    # ─────────────────────────────────────────────────────────────
    def _check_whitelist_enforcement(self, vote_events) -> AuditCheck:
        invalid = []
        for event in vote_events:
            voter = event["args"]["voter"]
            if not self.voting_service.is_whitelisted(voter):
                invalid.append(voter)
        if invalid:
            return AuditCheck(
                check_name="Whitelist Enforcement",
                status="FAILED",
                details=f"Non-whitelisted voters: {invalid}",
            )
        return AuditCheck(
            check_name="Whitelist Enforcement",
            status="PASSED",
            details="All voters whitelisted",
        )

    # ─────────────────────────────────────────────────────────────
    def _check_candidate_validation(self, vote_events) -> AuditCheck:
        candidate_map = {
            c.address.lower()
            for c in self.voting_service.get_candidates()
        }
        invalid = [
            event["args"]["candidate"].lower()
            for event in vote_events
            if event["args"]["candidate"].lower() not in candidate_map
        ]
        if invalid:
            return AuditCheck(
                check_name="Candidate Validation",
                status="FAILED",
                details=f"Invalid candidates: {invalid}",
            )
        return AuditCheck(
            check_name="Candidate Validation",
            status="PASSED",
            details="All votes target registered candidates",
        )

    # ─────────────────────────────────────────────────────────────
    def _check_stage_enforcement(
        self,
        vote_events,
        deploy_block: int = 0,
    ) -> AuditCheck:
        """
        FIX: Проверяет, что все голоса были поданы в период между
        событиями VotingStarted и VotingFinished.

        Раньше метод проверял только текущую стадию контракта —
        это давало PASSED при любом ACTIVE/FINISHED состоянии,
        не проверяя реальные блоки событий.

        Алгоритм:
        1. Получаем блок события VotingStarted.
        2. Получаем блок события VotingFinished (или latest, если ещё идёт).
        3. Проверяем, что blockNumber каждого VoteCast попадает в диапазон.
        4. Если события не найдены в ABI — fallback к проверке стадии.
        """
        contract = self.voting_service.contract
        latest = self.voting_service.provider.w3.eth.block_number

        try:
            started_events = contract.events.VotingStarted.get_logs(
                from_block=deploy_block, to_block=latest,
            )
            finished_events = contract.events.VotingFinished.get_logs(
                from_block=deploy_block, to_block=latest,
            )
        except Exception as exc:
            # VotingStarted/VotingFinished нет в ABI — деградируем к
            # проверке текущей стадии (минимальная гарантия)
            logger.warning(
                "Stage events not available in ABI (%s), "
                "falling back to stage check", exc,
            )
            return self._check_stage_enforcement_fallback(vote_events)

        if not started_events:
            if vote_events:
                return AuditCheck(
                    check_name="Stage Enforcement",
                    status="FAILED",
                    details=(
                        "VoteCast events found but VotingStarted "
                        "event is missing — votes cast before voting began"
                    ),
                )
            return AuditCheck(
                check_name="Stage Enforcement",
                status="PASSED",
                details="No votes cast, voting never started",
            )

        start_block: int = started_events[0]["blockNumber"]
        end_block: int = (
            finished_events[0]["blockNumber"]
            if finished_events
            else latest
        )

        invalid = [
            f"block={ev['blockNumber']}"
            for ev in vote_events
            if not (start_block <= ev["blockNumber"] <= end_block)
        ]

        if invalid:
            return AuditCheck(
                check_name="Stage Enforcement",
                status="FAILED",
                details=(
                    f"Votes outside valid range "
                    f"[{start_block}, {end_block}]: {invalid}"
                ),
            )
        return AuditCheck(
            check_name="Stage Enforcement",
            status="PASSED",
            details=(
                f"All {len(vote_events)} vote(s) within "
                f"valid range [{start_block}, {end_block}]"
            ),
        )

    def _check_stage_enforcement_fallback(self, vote_events) -> AuditCheck:
        """Запасная проверка стадии без анализа блоков."""
        current_stage = self.voting_service.get_stage()
        if current_stage.name not in ("ACTIVE", "FINISHED"):
            return AuditCheck(
                check_name="Stage Enforcement",
                status="FAILED",
                details="Voting was never activated",
            )
        return AuditCheck(
            check_name="Stage Enforcement",
            status="WARNING",
            details=(
                "Stage is valid but block-level verification unavailable "
                "(VotingStarted/VotingFinished events not in ABI)"
            ),
        )

    # ─────────────────────────────────────────────────────────────
    def _check_vote_count_integrity(self, vote_events) -> AuditCheck:
        counted_from_events = len(vote_events)
        candidates = self.voting_service.get_candidates()
        counted_onchain = sum(c.vote_count for c in candidates)
        if counted_from_events != counted_onchain:
            return AuditCheck(
                check_name="Vote Count Integrity",
                status="FAILED",
                details=(
                    f"Events={counted_from_events} "
                    f"OnChain={counted_onchain}"
                ),
            )
        return AuditCheck(
            check_name="Vote Count Integrity",
            status="PASSED",
            details=f"Votes verified: {counted_onchain}",
        )