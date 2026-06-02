"""
AppController.
Главный facade между UI и backend.
UI никогда не работает с Web3 напрямую.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from src.core.audit_service import AuditService
from src.core.compiler_service import CompilerService
from src.core.geth_manager import GethManager
from src.core.models import Candidate, SessionContext, VoteReceipt, Voter
from src.core.voting_service import VotingService
from src.core.web3_provider import Web3Provider
from src.utils.config import get_env_config
from src.utils.crypto import generate_test_voters
from src.utils.logger import archive_session_log, get_logger

logger = get_logger(__name__)


class AppController:
    """Главный orchestrator приложения."""

    def __init__(self) -> None:
        self.env = get_env_config()
        self.session = SessionContext()

        self.geth = GethManager(
            rpc_host=self.env.rpc_host,
            rpc_port=self.env.rpc_port,
            network_id=self.env.network_id,
        )
        # FIX: UI-callback для уведомления об аварийной остановке ноды
        self._crash_ui_callback: Optional[Callable[[], None]] = None
        self.geth.set_crash_callback(self._on_geth_crash)

        self.provider = Web3Provider(self.env.rpc_url)
        self.compiler = CompilerService()
        self.voting_service = VotingService(self.provider)
        self.audit_service = AuditService(self.voting_service)

    # ─────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────
    def startup(self) -> None:
        logger.info("Application startup")
        self.geth.start()
        self.provider.connect()
        if not self.provider.wait_for_rpc():
            raise RuntimeError("Ethereum RPC unavailable")
        logger.info("Application ready")

    def shutdown(self) -> None:
        logger.info("Application shutdown")
        try:
            if self.session.session_id:
                archive_session_log(self.session.session_id)
        finally:
            self.geth.stop()

    # ─────────────────────────────────────────────────────────────
    # UI crash callback
    # ─────────────────────────────────────────────────────────────
    def set_crash_ui_callback(self, cb: Callable[[], None]) -> None:
        """
        FIX: Регистрирует callback, который будет вызван из фонового потока
        при аварийной остановке geth. MainWindow использует это для
        отображения ошибки в UI через QueuedConnection.
        """
        self._crash_ui_callback = cb

    # ─────────────────────────────────────────────────────────────
    # Session
    # ─────────────────────────────────────────────────────────────
    def create_session(self, title: str = "MYCELIUM Session") -> str:
        session_id = str(uuid.uuid4())
        self.session.reset()
        self.session.session_id = session_id
        logger.info("Session created: %s", session_id)
        return session_id

    def get_session_summary(self) -> dict:
        return {
            "session_id": self.session.session_id,
            "contract_address": self.session.contract_address,
            "candidate_count": len(self.session.candidates),
            "voter_count": len(self.session.voters),
        }

    # ─────────────────────────────────────────────────────────────
    # Compile / Deploy
    # ─────────────────────────────────────────────────────────────
    def compile_contract(self) -> None:
        abi, bytecode = self.compiler.compile_contract()
        self.session.abi = abi
        self.voting_service.abi = abi
        self.voting_service.bytecode = bytecode
        logger.info("Contract compiled")

    def deploy_contract(self, admin_private_key: str) -> str:
        if not self.session.abi:
            raise RuntimeError("Contract not compiled")
        contract_address = self.voting_service.deploy_contract(
            admin_private_key=admin_private_key,
            abi=self.voting_service.abi,
            bytecode=self.voting_service.bytecode,
        )
        self.session.contract_address = contract_address
        self.session.deploy_block = self.provider.get_block_number() or 0
        logger.info("Contract deployed: %s", contract_address)
        return contract_address

    # ─────────────────────────────────────────────────────────────
    # Candidates
    # ─────────────────────────────────────────────────────────────
    def add_candidate(
        self,
        admin_private_key: str,
        name: str,
        party: str,
        address: str,
    ) -> str:
        candidate = Candidate(name=name, party=party, address=address)
        tx_hash = self.voting_service.add_candidate(admin_private_key, candidate)
        self.session.candidates.append(candidate)
        logger.info("Candidate added: %s", candidate.address)
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Voters
    # ─────────────────────────────────────────────────────────────
    def generate_voters(self, count: int) -> list[Voter]:
        generated = generate_test_voters(count)
        voters: list[Voter] = []
        for item in generated:
            voter = Voter(
                address=item["address"],
                private_key=item["private_key"],
            )
            voters.append(voter)
        self.session.voters.extend(voters)
        logger.info("Generated %d voters", len(voters))
        return voters

    def whitelist_voters(self, admin_private_key: str) -> str:
        addresses = [v.address for v in self.session.voters]
        tx_hash = self.voting_service.add_voters_batch(admin_private_key, addresses)
        logger.info("Whitelist updated")
        return tx_hash

    def export_voters(self, output_path: str) -> None:
        payload = {
            "warning": "This file contains private keys. Keep it secret.",
            "voters": [voter.to_export_dict() for voter in self.session.voters],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        logger.warning("Voters exported: %s", output_path)

    def import_voters(self, input_path: str) -> int:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        imported = 0
        for item in data.get("voters", []):
            voter = Voter(
                address=item["address"],
                private_key=item.get("private_key"),
                has_voted=item.get("has_voted", False),
            )
            self.session.voters.append(voter)
            imported += 1
        logger.info("Imported voters: %d", imported)
        return imported

    # ─────────────────────────────────────────────────────────────
    # Stages
    # ─────────────────────────────────────────────────────────────
    def start_voting(self, admin_private_key: str) -> str:
        tx_hash = self.voting_service.start_voting(admin_private_key)
        logger.info("Voting ACTIVE")
        return tx_hash

    def finish_voting(self, admin_private_key: str) -> str:
        tx_hash = self.voting_service.finish_voting(admin_private_key)
        logger.info("Voting FINISHED")
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Voting
    # ─────────────────────────────────────────────────────────────
    def cast_vote(
        self,
        voter_private_key: str,
        candidate_address: str,
    ) -> VoteReceipt:
        if not self.session.session_id:
            raise RuntimeError("No active session")
        receipt = self.voting_service.cast_vote(
            voter_private_key=voter_private_key,
            candidate_address=candidate_address,
            session_id=self.session.session_id,
        )
        logger.info("Vote submitted: %s", receipt.tx_hash)
        return receipt

    # ─────────────────────────────────────────────────────────────
    # Audit
    # ─────────────────────────────────────────────────────────────
    def run_audit(self):
        if not self.session.session_id:
            raise RuntimeError("No active session")
        # FIX: передаём deploy_block для реальной проверки стадий по блокам
        return self.audit_service.run_audit(
            self.session.session_id,
            deploy_block=self.session.deploy_block,
        )

    def get_results(self):
        return self.audit_service.build_results()

    def get_winner(self):
        return self.audit_service.detect_winner()

    def export_results(self, output_path: str) -> None:
        report = self.run_audit()
        results = self.get_results()
        winner = self.get_winner()
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "contract_address": self.session.contract_address,
            "results": [
                {
                    "name": c.name,
                    "party": c.party,
                    "address": c.address,
                    "votes": c.vote_count,
                }
                for c in results
            ],
            "winner": str(winner),
            "audit": report.to_dict(),
        }
        Path(output_path).write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        logger.info("Results exported: %s", output_path)

    # ─────────────────────────────────────────────────────────────
    # Read API
    # ─────────────────────────────────────────────────────────────
    def get_stage(self):
        return self.voting_service.get_stage()

    def get_candidates(self):
        return self.voting_service.get_candidates()

    def is_whitelisted(self, address: str) -> bool:
        return self.voting_service.is_whitelisted(address)

    def has_voted(self, address: str) -> bool:
        return self.voting_service.has_voted(address)

    def get_rpc_status(self) -> bool:
        return self.provider.is_connected()

    def get_block_number(self):
        return self.provider.get_block_number()

    # ─────────────────────────────────────────────────────────────
    def _on_geth_crash(self) -> None:
        logger.critical("Geth node crashed")
        # FIX: уведомляем UI через зарегистрированный callback.
        # Вызов идёт из фонового потока — MainWindow обязан пробросить
        # его в main thread через QMetaObject.invokeMethod + QueuedConnection.
        if self._crash_ui_callback:
            self._crash_ui_callback()