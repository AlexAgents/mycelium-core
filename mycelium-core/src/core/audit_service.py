"""
AuditService.

Полный event-based аудит голосования.
Поддерживает staged-аудит (pre-vote / live / final).
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from web3 import Web3

from src.core.models import AuditCheck, AuditReport, ElectionStage
from src.core.voting_service import VotingService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    def __init__(self, voting_service: VotingService) -> None:
        self.voting_service = voting_service

    # ─────────────────────────────────────────────────────────────
    # Публичный API
    # ─────────────────────────────────────────────────────────────
    def run_audit(
        self,
        session_id: str,
        deploy_block: int = 0,
    ) -> AuditReport:
        """Полный аудит (все проверки)."""
        return self._run_checks(
            session_id, deploy_block, mode="full"
        )

    def run_pre_vote_audit(
        self,
        session_id: str,
        deploy_block: int = 0,
    ) -> AuditReport:
        """Проверки до начала голосования."""
        return self._run_checks(
            session_id, deploy_block, mode="pre"
        )

    def run_live_audit(
        self,
        session_id: str,
        deploy_block: int = 0,
    ) -> AuditReport:
        """Проверки во время голосования."""
        return self._run_checks(
            session_id, deploy_block, mode="live"
        )

    def run_final_audit(
        self,
        session_id: str,
        deploy_block: int = 0,
    ) -> AuditReport:
        """Полная финальная проверка."""
        return self._run_checks(
            session_id, deploy_block, mode="final"
        )

    # ─────────────────────────────────────────────────────────────
    def _run_checks(
        self,
        session_id: str,
        deploy_block: int,
        mode: str,
    ) -> AuditReport:
        logger.info("Running %s audit", mode)

        checks: list[AuditCheck] = []
        current_stage = self._get_current_stage()
        vote_events = None

        # ── Проверки перед голосованием ─────────────────────
        if mode in ("pre", "full"):
            checks.append(self._check_candidate_count())
            checks.append(self._check_whitelist_populated())
            checks.append(
                self._check_stage_valid_for_prevote(current_stage)
            )

        # ── События ─────────────────────────────────────────
        if mode in ("live", "final", "full"):
            try:
                vote_events = self._get_vote_events(deploy_block)
            except Exception as exc:
                checks.append(AuditCheck(
                    check_name="Event Retrieval",
                    status="FAILED",
                    details=f"Cannot load VoteCast events: {exc}",
                ))

        # ── Проверки Live ──────────────────────────────────
        if mode in ("live", "full") and vote_events is not None:
            checks.append(
                self._check_double_vote(vote_events)
            )
            checks.append(
                self._check_whitelist_enforcement(vote_events)
            )

        # ── Проверки Final ─────────────────────────────────
        if mode in ("final", "full") and vote_events is not None:
            checks.append(
                self._check_candidate_validation(vote_events)
            )
            checks.append(
                self._check_stage_enforcement(
                    vote_events, deploy_block
                )
            )
            checks.append(
                self._check_vote_count_integrity(vote_events)
            )
            checks.append(
                self._check_owner_actions(deploy_block)
            )
        # ── Информация о пропущенных проверках ──────────────
        if mode == "pre":
            for name in (
                "Double Vote Protection",
                "Stage Enforcement",
                "Vote Count Integrity",
            ):
                checks.append(AuditCheck(
                    check_name=name,
                    status="SKIPPED",
                    details=(
                        "Not applicable in pre-vote stage"
                    ),
                ))

        if mode == "live":
            for name in (
                "Vote Count Integrity",
                "Stage Enforcement",
            ):
                checks.append(AuditCheck(
                    check_name=name,
                    status="SKIPPED",
                    details=(
                        "Only available after voting is finished"
                    ),
                ))

        # Дедупликация по check_name (оставляем первый)
        seen = set()
        unique_checks: list[AuditCheck] = []
        for c in checks:
            if c.check_name not in seen:
                seen.add(c.check_name)
                unique_checks.append(c)

        report = AuditReport(
            session_id=session_id,
            audit_timestamp=datetime.now(timezone.utc),
            checks=unique_checks,
        )

        logger.info(
            "Audit (%s) finished passed=%s failed=%d",
            mode, report.all_passed, report.failed_count,
        )
        return report

    # ─────────────────────────────────────────────────────────────
    # Результаты
    # ─────────────────────────────────────────────────────────────
    def build_results(self):
        candidates = self.voting_service.get_candidates()
        return sorted(
            candidates, key=lambda c: c.vote_count, reverse=True
        )

    def detect_winner(self):
        results = self.build_results()
        if not results:
            return None
        top = results[0]
        tied = [
            c for c in results
            if c.vote_count == top.vote_count
        ]
        if len(tied) > 1:
            return {"type": "tie", "candidates": tied}
        return {"type": "winner", "candidate": top}

    # ─────────────────────────────────────────────────────────────
    # Вспомогательные методы
    # ─────────────────────────────────────────────────────────────
    def _get_current_stage(self) -> Optional[ElectionStage]:
        try:
            return self.voting_service.get_stage()
        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────
    # Извлечение событий
    # ─────────────────────────────────────────────────────────────
    def _get_vote_events(self, from_block: int = 0):
        contract = self.voting_service.contract
        if contract is None:
            raise RuntimeError("Contract not loaded")

        latest = (
            self.voting_service.provider.w3.eth.block_number
        )
        events = contract.events.VoteCast.get_logs(
            from_block=from_block, to_block=latest,
        )
        logger.info("Loaded %d VoteCast events", len(events))
        return events

    # ─────────────────────────────────────────────────────────────
    # Проверки перед голосованием
    # ─────────────────────────────────────────────────────────────
    def _check_candidate_count(self) -> AuditCheck:
        """Проверяет что зарегистрировано >= 2 кандидатов."""
        try:
            candidates = self.voting_service.get_candidates()
            count = len(candidates)
            if count < 2:
                return AuditCheck(
                    check_name="Candidate Count",
                    status="FAILED",
                    details=(
                        f"Only {count} candidate(s) registered, "
                        "minimum 2 required"
                    ),
                )
            return AuditCheck(
                check_name="Candidate Count",
                status="PASSED",
                details=f"{count} candidates registered",
            )
        except Exception as exc:
            return AuditCheck(
                check_name="Candidate Count",
                status="FAILED",
                details=f"Cannot check candidates: {exc}",
            )

    def _check_whitelist_populated(self) -> AuditCheck:
        """Проверяет что whitelist не пуст."""
        try:
            contract = self.voting_service.contract
            if contract is None:
                return AuditCheck(
                    check_name="Whitelist Populated",
                    status="FAILED",
                    details="Contract not loaded",
                )
            voters = (
                contract.functions.getVoterAddresses().call()
            )
            if not voters:
                return AuditCheck(
                    check_name="Whitelist Populated",
                    status="WARNING",
                    details="Whitelist is empty",
                )
            return AuditCheck(
                check_name="Whitelist Populated",
                status="PASSED",
                details=f"{len(voters)} voter(s) whitelisted",
            )
        except Exception as exc:
            return AuditCheck(
                check_name="Whitelist Populated",
                status="FAILED",
                details=f"Cannot check whitelist: {exc}",
            )

    def _check_stage_valid_for_prevote(
        self, stage: Optional[ElectionStage]
    ) -> AuditCheck:
        if stage is None:
            return AuditCheck(
                check_name="Stage Check",
                status="WARNING",
                details="Cannot determine current stage",
            )
        if stage == ElectionStage.SETUP:
            return AuditCheck(
                check_name="Stage Check",
                status="PASSED",
                details="Contract is in Setup stage — ready",
            )
        return AuditCheck(
            check_name="Stage Check",
            status="WARNING",
            details=(
                f"Contract is already in {stage.name} stage"
            ),
        )

    def _check_owner_actions(
        self, deploy_block: int
    ) -> AuditCheck:
        """
        Проверяет, что все admin-действия
        (CandidateAdded, VoterWhitelisted, StageChanged)
        были вызваны от owner'а контракта.
        """
        contract = self.voting_service.contract
        if contract is None:
            return AuditCheck(
                check_name="Owner-only Administration",
                status="FAILED",
                details="Contract not loaded",
            )

        try:
            owner = self.voting_service.get_owner()
            latest = (
                self.voting_service.provider.w3.eth.block_number
            )

            unauthorized: list[str] = []

            # Проверяем события CandidateAdded
            try:
                ca_events = (
                    contract.events.CandidateAdded.get_logs(
                        from_block=deploy_block,
                        to_block=latest,
                    )
                )
                for ev in ca_events:
                    tx_hash = ev["transactionHash"]
                    tx = (
                        self.voting_service.provider.w3
                        .eth.get_transaction(tx_hash)
                    )
                    if tx["from"].lower() != owner.lower():
                        unauthorized.append(
                            f"CandidateAdded from "
                            f"{tx['from'][:10]}..."
                        )
            except Exception:
                pass

            # Проверяем события VoterWhitelisted
            try:
                vw_events = (
                    contract.events.VoterWhitelisted.get_logs(
                        from_block=deploy_block,
                        to_block=latest,
                    )
                )
                # VoterWhitelisted может быть много; проверяем только
                # отправителей уникальных TX-хэшей
                checked_txs: set = set()
                for ev in vw_events:
                    tx_hash = ev["transactionHash"]
                    if tx_hash in checked_txs:
                        continue
                    checked_txs.add(tx_hash)
                    tx = (
                        self.voting_service.provider.w3
                        .eth.get_transaction(tx_hash)
                    )
                    if tx["from"].lower() != owner.lower():
                        unauthorized.append(
                            f"VoterWhitelisted from "
                            f"{tx['from'][:10]}..."
                        )
            except Exception:
                pass

            # Проверяем события StageChanged
            try:
                sc_events = (
                    contract.events.StageChanged.get_logs(
                        from_block=deploy_block,
                        to_block=latest,
                    )
                )
                for ev in sc_events:
                    tx_hash = ev["transactionHash"]
                    tx = (
                        self.voting_service.provider.w3
                        .eth.get_transaction(tx_hash)
                    )
                    if tx["from"].lower() != owner.lower():
                        unauthorized.append(
                            f"StageChanged from "
                            f"{tx['from'][:10]}..."
                        )
            except Exception:
                pass

            if unauthorized:
                return AuditCheck(
                    check_name="Owner-only Administration",
                    status="FAILED",
                    details=(
                        f"Unauthorized actions detected: "
                        f"{unauthorized}"
                    ),
                )

            return AuditCheck(
                check_name="Owner-only Administration",
                status="PASSED",
                details=(
                    "All admin actions performed by owner"
                ),
            )

        except Exception as exc:
            return AuditCheck(
                check_name="Owner-only Administration",
                status="WARNING",
                details=f"Could not verify: {exc}",
            )

    # ─────────────────────────────────────────────────────────────
    # Проверки голосов
    # ─────────────────────────────────────────────────────────────
    def _check_double_vote(self, vote_events) -> AuditCheck:
        voters = [e["args"]["voter"] for e in vote_events]
        duplicates = [
            addr
            for addr, count in Counter(voters).items()
            if count > 1
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

    def _check_whitelist_enforcement(
        self, vote_events
    ) -> AuditCheck:
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

    def _check_candidate_validation(
        self, vote_events
    ) -> AuditCheck:
        candidate_map = {
            c.address.lower()
            for c in self.voting_service.get_candidates()
        }
        invalid = [
            event["args"]["candidate"].lower()
            for event in vote_events
            if event["args"]["candidate"].lower()
            not in candidate_map
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

    def _check_stage_enforcement(
        self, vote_events, deploy_block: int = 0,
    ) -> AuditCheck:
        contract = self.voting_service.contract
        latest = (
            self.voting_service.provider.w3.eth.block_number
        )

        try:
            started_events = (
                contract.events.VotingStarted.get_logs(
                    from_block=deploy_block, to_block=latest,
                )
            )
            finished_events = (
                contract.events.VotingFinished.get_logs(
                    from_block=deploy_block, to_block=latest,
                )
            )
        except Exception as exc:
            logger.warning(
                "Stage events not available (%s), fallback", exc
            )
            return self._check_stage_enforcement_fallback(
                vote_events
            )

        if not started_events:
            if vote_events:
                return AuditCheck(
                    check_name="Stage Enforcement",
                    status="FAILED",
                    details=(
                        "VoteCast events found but VotingStarted "
                        "event is missing"
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
            if not (
                start_block <= ev["blockNumber"] <= end_block
            )
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

    def _check_stage_enforcement_fallback(
        self, vote_events
    ) -> AuditCheck:
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
                "Stage is valid but block-level verification "
                "unavailable"
            ),
        )

    def _check_vote_count_integrity(
        self, vote_events
    ) -> AuditCheck:
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