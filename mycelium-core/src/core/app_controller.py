"""
AppController.

Главный фасад между UI и backend.
UI никогда не работает с Web3 напрямую.
"""
from __future__ import annotations

import shutil
import os
import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional
from web3 import Web3

from src.core.audit_service import AuditService
from src.core.compiler_service import CompilerService
from src.core.geth_manager import GethManager
from src.core.models import Candidate, SessionContext, VoteReceipt, Voter
from src.core.voting_service import VotingService
from src.core.web3_provider import Web3Provider
from src.core.error_parser import ErrorParser, ParsedError
from src.core.precheck import PrecheckResult, PrecheckStatus
from src.core.voter_status import VoterStatus
from src.utils.config import get_env_config
from src.utils.crypto import generate_test_voters
from src.utils.logger import archive_session_log, get_logger


logger = get_logger(__name__)


class AppController:
    """Главный оркестратор приложения."""

    def __init__(self) -> None:
        self.env = get_env_config()
        self.session = SessionContext()

        self.geth = GethManager(
            rpc_host=self.env.rpc_host,
            rpc_port=self.env.rpc_port,
            network_id=self.env.network_id,
        )

        self._crash_ui_callback: Optional[Callable[[], None]] = None
        self.geth.set_crash_callback(self._on_geth_crash)

        self.provider = Web3Provider(self.env.rpc_url)
        self.compiler = CompilerService()
        self.voting_service = VotingService(self.provider)
        self.audit_service = AuditService(self.voting_service)
        self.error_parser = ErrorParser()

    # ─────────────────────────────────────────────────────────────
    # Жизненный цикл
    # ─────────────────────────────────────────────────────────────
    def startup(self) -> None:
        logger.info("Application startup")
        self.geth.start()
        self.provider.connect()
        if not self.provider.wait_for_rpc():
            raise RuntimeError("Ethereum RPC unavailable")
        logger.info("Application ready")

    def get_chain_stats(self) -> dict:
        """
        Возвращает статистику по chain-data и архивам.

        Returns:
            {
                "size_bytes": int,           # размер chain-data в байтах
                "size_mb": float,            # тот же размер в МБ
                "deployed_contracts": int,   # сколько контрактов было задеплоено
                "archived_sessions": int,    # сколько архивных сессий
            }
        """
        from src.utils.paths import CHAIN_ACTIVE, LOGS_ARCHIVE

        # Размер chain-data
        size_bytes = 0
        if CHAIN_ACTIVE.exists():
            for root, _, files in os.walk(CHAIN_ACTIVE):
                for f in files:
                    try:
                        size_bytes += os.path.getsize(
                            os.path.join(root, f)
                        )
                    except OSError:
                        pass

        # Количество архивных сессий = подпапок в logs/archive/
        archived_sessions = 0
        if LOGS_ARCHIVE.exists():
            archived_sessions = sum(
                1 for entry in LOGS_ARCHIVE.iterdir()
                if entry.is_dir()
            )

        # Количество задеплоенных контрактов:
        # быстрый способ — через текущее количество архивных сессий + 1 (текущая)
        # точный способ требует разбора всех TX, дорого
        deployed_contracts = archived_sessions + (
            1 if self.session.contract_address else 0
        )

        return {
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "deployed_contracts": deployed_contracts,
            "archived_sessions": archived_sessions,
        }

    def reset_blockchain_data(
        self,
        delete_archived_logs: bool = False,
    ) -> None:
        """
        Полный сброс blockchain-данных.

        Если файлы заблокированы и удалить нельзя — RuntimeError
        с понятным сообщением для пользователя.
        """
        from src.utils.paths import CHAIN_ACTIVE, LOGS_ARCHIVE
        import time

        logger.info("Resetting blockchain data...")

        # 1. Закрыть web3 connection
        try:
            if self.provider._w3 is not None:
                self.provider._w3 = None
        except Exception:
            pass

        # 2. Остановить Geth (с taskkill внутри)
        try:
            self.geth.stop()
        except Exception as exc:
            logger.warning("Geth stop during reset failed: %s", exc)

        # Дополнительная пауза для Windows
        time.sleep(2.0)

        # 3. Удалить chain-data
        if CHAIN_ACTIVE.exists():
            ok = self._rmtree_with_retry(CHAIN_ACTIVE, attempts=8)
            if not ok:
                # Не удалось. Формируем сообщение.
                paths_to_clean = [str(CHAIN_ACTIVE)]
                if delete_archived_logs and LOGS_ARCHIVE.exists():
                    paths_to_clean.append(str(LOGS_ARCHIVE))

                paths_str = "\n".join(f"  - {p}" for p in paths_to_clean)
                raise RuntimeError(
                    "MANUAL_CLEANUP_REQUIRED|"
                    + paths_str
                )
            logger.info("chain-data/active/ deleted")

        # 4. Архивные логи (опционально)
        if delete_archived_logs and LOGS_ARCHIVE.exists():
            ok = self._rmtree_with_retry(LOGS_ARCHIVE, attempts=5)
            if ok:
                LOGS_ARCHIVE.mkdir(parents=True, exist_ok=True)
                logger.info("logs/archive/ deleted")
            else:
                logger.warning(
                    "Could not delete logs/archive/, skipping"
                )

        # 5. Перезапустить Geth
        try:
            self.geth.start()
            self.provider.connect()
            if not self.provider.wait_for_rpc():
                raise RuntimeError("Geth RPC unavailable after reset")
        except Exception as exc:
            raise RuntimeError(
                f"Failed to restart Geth: {exc}"
            ) from exc

        # 6. Новая сессия
        self.new_session()
        logger.info("Blockchain data reset completed")

    @staticmethod
    def _rmtree_with_retry(path, attempts: int = 5) -> bool:
        """
        Удаление папки с retry для Windows.

        На Windows файлы могут оставаться залоченными несколько секунд
        после завершения процесса, который их открывал.

        Returns:
            True если удалено успешно, False если все попытки исчерпаны.
        """
        import time
        import stat

        def _on_error(func, target_path, exc_info):
            """Снимаем read-only флаг и пробуем повторно."""
            try:
                os.chmod(target_path, stat.S_IWRITE)
                func(target_path)
            except Exception:
                pass

        for attempt in range(attempts):
            try:
                shutil.rmtree(path, onerror=_on_error)
                if not path.exists():
                    return True
            except PermissionError as exc:
                logger.debug(
                    "rmtree attempt %d/%d failed: %s",
                    attempt + 1, attempts, exc,
                )
            except FileNotFoundError:
                return True
            except Exception as exc:
                logger.warning(
                    "rmtree unexpected error: %s", exc
                )

            # Прогрессивная задержка: 1с, 1.5с, 2с, 2.5с, 3с...
            time.sleep(1.0 + 0.5 * attempt)

        return False

    def shutdown(self) -> None:
        logger.info("Application shutdown")
        try:
            if self.session.session_id:
                archive_session_log(self.session.session_id)
        finally:
            self.geth.stop()

    # ─────────────────────────────────────────────────────────────
    def set_crash_ui_callback(self, cb: Callable[[], None]) -> None:
        self._crash_ui_callback = cb

    # ─────────────────────────────────────────────────────────────
    # Сессия
    # ─────────────────────────────────────────────────────────────
    def create_session(self, title: str = "MYCELIUM Session") -> str:
        session_id = str(uuid.uuid4())
        self.session.reset()
        self.session.session_id = session_id
        self.voting_service.reset()
        logger.info("Session created: %s", session_id)
        return session_id

    def new_session(self) -> str:
        old_id = self.session.session_id
        if old_id:
            archive_session_log(old_id)
            logger.info("Previous session archived: %s", old_id)
        new_id = self.create_session()
        logger.info("New session started: %s", new_id)
        return new_id

    def get_session_summary(self) -> dict:
        return {
            "session_id": self.session.session_id,
            "contract_address": self.session.contract_address,
            "candidate_count": len(self.session.candidates),
            "voter_count": len(self.session.voters),
        }

    # ─────────────────────────────────────────────────────────────
    # Компиляция / Деплой
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
        self.session.deploy_block = (
            self.provider.get_block_number() or 0
        )
        logger.info("Contract deployed: %s", contract_address)
        return contract_address

    # ─────────────────────────────────────────────────────────────
    # Кандидаты
    # ─────────────────────────────────────────────────────────────
    def add_candidate(
        self,
        admin_private_key: str,
        name: str,
        party: str,
        address: str,
    ) -> str:
        candidate = Candidate(name=name, party=party, address=address)
        tx_hash = self.voting_service.add_candidate(
            admin_private_key, candidate
        )
        self.session.candidates.append(candidate)
        logger.info("Candidate added: %s", candidate.address)
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Избиратели
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
        tx_hash = self.voting_service.add_voters_batch(
            admin_private_key, addresses
        )
        logger.info("Whitelist updated")
        return tx_hash

    def export_voters(self, output_path: str) -> None:
        payload = {
            "warning": (
                "This file contains private keys. Keep it secret."
            ),
            "voters": [
                voter.to_export_dict()
                for voter in self.session.voters
            ],
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
    # Финансирование
    # ─────────────────────────────────────────────────────────────
    def fund_voter(
        self,
        admin_private_key: str,
        voter_address: str,
        amount_wei: int,
    ) -> str:
        tx_hash = self.voting_service.fund_account(
            admin_private_key, voter_address, amount_wei,
        )
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Баланс
    # ─────────────────────────────────────────────────────────────
    def get_balance_wei(self, address: str) -> int:
        return self.provider.get_balance(address)
    
    def get_balance_eth(self, address: str) -> str:
        """
        Возвращает баланс в ETH в компактном формате.

        Форматы:
            >= 1T      -> "1.23T"
            >= 1B      -> "1.23B"
            >= 1M      -> "1.23M"
            >= 1K      -> "1.23K"
            >= 1       -> "1.2345"
            >= 0.0001  -> "0.001234"
            > 0        -> "0.00000012"
            == 0       -> "0"
        """
        wei = self.get_balance_wei(address)
        eth = wei / 10 ** 18

        if eth == 0:
            return "0"
        elif eth >= 1e15:
            # dev-аккаунт может быть ~1e59
            return f"{eth:.2e}"
        elif eth >= 1e12:
            return f"{eth / 1e12:.2f}T"
        elif eth >= 1e9:
            return f"{eth / 1e9:.2f}B"
        elif eth >= 1e6:
            return f"{eth / 1e6:.2f}M"
        elif eth >= 1e3:
            return f"{eth / 1e3:.2f}K"
        elif eth >= 1:
            return f"{eth:.4f}"
        elif eth >= 0.0001:
            return f"{eth:.6f}"
        else:
            return f"{eth:.8f}"
        
    def get_dev_account_address(self) -> Optional[str]:
        """
        Возвращает адрес dev-аккаунта Geth (первый из eth.accounts).
        В dev-mode этот аккаунт имеет огромный баланс.
        """
        accounts = self.provider.get_accounts()
        if accounts:
            return accounts[0]
        return None

    def fund_from_dev(
        self,
        target_address: str,
        amount_eth: float = 100.0,
    ) -> str:
        """
        Переводит ETH с разблокированного dev-аккаунта Geth
        на указанный адрес. Работает только в dev-mode.

        Returns:
            tx_hash (hex string).

        Raises:
            RuntimeError — если не dev-mode или нет dev-аккаунта.
        """
        if self.geth.mode != "dev":
            raise RuntimeError(
                "fund_from_dev is available only in Geth dev mode"
            )

        accounts = self.provider.get_accounts()
        if not accounts:
            raise RuntimeError("No dev account available in Geth")

        dev_addr = accounts[0]
        target = Web3.to_checksum_address(target_address)
        amount_wei = int(amount_eth * 10 ** 18)

        if dev_addr.lower() == target.lower():
            raise RuntimeError(
                "Source and target addresses are identical"
            )

        w3 = self.provider.w3
        tx_hash = w3.eth.send_transaction({
            "from": dev_addr,
            "to": target,
            "value": amount_wei,
        })
        w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        logger.info(
            "Funded %s with %.4f ETH from dev account (tx=%s)",
            target[:10], amount_eth, tx_hash.hex()[:16],
        )
        return tx_hash.hex()
        
    # ─────────────────────────────────────────────────────────────
    # Адрес из ключа (UI не импортирует eth_account)
    # ─────────────────────────────────────────────────────────────
    def get_address_from_key(self, private_key: str) -> str:
        from src.utils.crypto import address_from_private_key
        return address_from_private_key(private_key)

    def validate_private_key(self, key: str) -> bool:
        """Валидация ключа без импорта eth_account в UI."""
        from src.utils.validators import is_valid_private_key
        return is_valid_private_key(key)

    # ─────────────────────────────────────────────────────────────
    # Информация о Geth
    # ─────────────────────────────────────────────────────────────
    def get_geth_mode(self) -> str:
        return self.geth.mode

    # ─────────────────────────────────────────────────────────────
    # Стадии голосования
    # ─────────────────────────────────────────────────────────────
    def check_start_voting_ready(self) -> tuple[bool, str]:
        """
        Проверяет, можно ли вызвать startVoting().

        Returns:
            (ready, reason_key)
            reason_key — ключ i18n для показа пользователю,
            пустой если ready=True.

        Бизнес-логика: контракт требует >= 2 кандидатов + populated whitelist.
        """
        if not self.session.contract_address:
            return False, "admin.dialog.cannot_start.no_contract"

        try:
            candidates = self.voting_service.get_candidates()
        except Exception:
            return False, "admin.dialog.cannot_start.no_contract"

        if len(candidates) < 2:
            return False, "admin.dialog.cannot_start.few_candidates"

        # Проверяем для UX: иначе никто не сможет проголосовать.
        try:
            contract = self.voting_service.contract
            voters = contract.functions.getVoterAddresses().call()
            if not voters:
                return False, "admin.dialog.cannot_start.no_whitelist"
        except Exception:
            pass

        return True, ""

    def get_candidates_count_onchain(self) -> int:
        """Количество on-chain зарегистрированных кандидатов."""
        try:
            return len(self.voting_service.get_candidates())
        except Exception:
            return 0

    def start_voting(self, admin_private_key: str) -> str:
        tx_hash = self.voting_service.start_voting(admin_private_key)
        logger.info("Voting ACTIVE")
        return tx_hash

    def finish_voting(self, admin_private_key: str) -> str:
        tx_hash = self.voting_service.finish_voting(admin_private_key)
        logger.info("Voting FINISHED")
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Голосование
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
    # Аудит
    # ─────────────────────────────────────────────────────────────
    def run_audit(self):
        if not self.session.session_id:
            raise RuntimeError("No active session")
        return self.audit_service.run_audit(
            self.session.session_id,
            deploy_block=self.session.deploy_block,
        )

    def get_results(self):
        return self.audit_service.build_results()

    def get_winner(self):
        return self.audit_service.detect_winner()

    def build_full_report(self) -> dict:
        """
        Строит полный отчёт по сессии: результаты + аудит + winner.

        Один источник истины для:
            - копирования в буфер обмена (Audit -> Copy Report)
            - экспорта JSON (Audit -> JSON)
            - экспорта CSV (Audit -> CSV)

        Raises:
            RuntimeError — если нет активной сессии.
        """
        if not self.session.session_id:
            raise RuntimeError("No active session")

        report = self.run_audit()
        results = self.get_results()
        winner = self.get_winner()

        try:
            stage = self.get_stage().name
        except Exception:
            stage = None

        # Сериализация winner
        winner_serialized: Optional[dict]
        if winner is None:
            winner_serialized = None
        elif winner["type"] == "tie":
            winner_serialized = {
                "type": "tie",
                "candidates": [
                    {
                        "name": c.name,
                        "party": c.party,
                        "address": c.address,
                        "votes": c.vote_count,
                    }
                    for c in winner["candidates"]
                ],
            }
        else:
            c = winner["candidate"]
            winner_serialized = {
                "type": "winner",
                "candidate": {
                    "name": c.name,
                    "party": c.party,
                    "address": c.address,
                    "votes": c.vote_count,
                },
            }

        return {
            "session_id": self.session.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract_address": self.session.contract_address,
            "stage": stage,
            "deploy_block": self.session.deploy_block,
            "results": [
                {
                    "name": c.name,
                    "party": c.party,
                    "address": c.address,
                    "votes": c.vote_count,
                }
                for c in results
            ],
            "winner": winner_serialized,
            "audit": report.to_dict(),
        }

    def export_results(self, output_path: str) -> None:
        """Экспортирует полный отчёт (results + audit) в JSON."""
        payload = self.build_full_report()
        Path(output_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Results exported: %s", output_path)

    def export_results_csv(self, output_path: str) -> None:
        """
        Экспортирует отчёт в CSV.
        Структура:
            [Section] Results
            Name, Party, Address, Votes
            ...
            [Section] Winner
            ...
            [Section] Audit
            Check, Status, Details
            ...
        """
        payload = self.build_full_report()

        with open(
            output_path, "w", encoding="utf-8", newline=""
        ) as f:
            writer = csv.writer(f)

            # ── Header info ──────────────────────────────────
            writer.writerow(["Session ID", payload["session_id"]])
            writer.writerow(["Timestamp", payload["timestamp"]])
            writer.writerow(
                ["Contract", payload["contract_address"] or ""]
            )
            writer.writerow(["Stage", payload["stage"] or ""])
            writer.writerow([])

            # ── Results ──────────────────────────────────────
            writer.writerow(["[Results]"])
            writer.writerow(["Name", "Party", "Address", "Votes"])
            for c in payload["results"]:
                writer.writerow([
                    c["name"], c["party"], c["address"], c["votes"]
                ])
            writer.writerow([])

            # ── Winner ───────────────────────────────────────
            writer.writerow(["[Winner]"])
            winner = payload["winner"]
            if winner is None:
                writer.writerow(["No winner"])
            elif winner["type"] == "tie":
                names = ", ".join(
                    c["name"] for c in winner["candidates"]
                )
                writer.writerow([f"Tie: {names}"])
            else:
                c = winner["candidate"]
                writer.writerow([f"{c['name']} ({c['party']})"])
            writer.writerow([])

            # ── Audit ────────────────────────────────────────
            writer.writerow(["[Audit]"])
            writer.writerow(["Check", "Status", "Details"])
            for check in payload["audit"]["checks"]:
                writer.writerow([
                    check["check_name"],
                    check["status"],
                    check["details"],
                ])

        logger.info("Results CSV exported: %s", output_path)

    # ─────────────────────────────────────────────────────────────
    # Парсинг ошибок
    # ─────────────────────────────────────────────────────────────

    def parse_rpc_error(self, error_text: str) -> dict:
        """
        Парсит RPC/контрактную ошибку через ErrorParser.
        Возвращает структуру с i18n-ключами — UI вызывает t() сам.
        """
        parsed: ParsedError = self.error_parser.parse(error_text)
        return {
            "message_key": parsed.message_key,
            "raw_message": parsed.raw_message,
            "action_key": parsed.action_key,
            "action_id": parsed.action_id,
        }

    # ─────────────────────────────────────────────────────────────
    # Предварительные проверки перед голосованием
    # ─────────────────────────────────────────────────────────────
    def precheck_vote(
        self,
        voter_private_key: str,
        min_balance_wei: int = 300_000 * 1_000_000_000,
    ) -> PrecheckResult:
        """
        Полная проверка готовности избирателя к голосованию.

        Объединяет все проверки, которые раньше были в VoteTab._cast_vote.
        UI получает структурированный результат и показывает понятное сообщение.

        Args:
            voter_private_key: приватный ключ избирателя
            min_balance_wei: минимально необходимый баланс для оплаты газа

        Returns:
            PrecheckResult со статусом и пояснением.
        """
        if not self.validate_private_key(voter_private_key):
            return PrecheckResult(
                status=PrecheckStatus.INVALID_KEY,
            )

        try:
            address = self.get_address_from_key(voter_private_key)
        except Exception as exc:
            return PrecheckResult(
                status=PrecheckStatus.INVALID_KEY,
                error_text=str(exc),
            )

        # Контракт должен быть развёрнут
        if not self.session.contract_address:
            return PrecheckResult(
                status=PrecheckStatus.NO_CONTRACT,
                address=address,
            )

        try:
            if not self.is_whitelisted(address):
                return PrecheckResult(
                    status=PrecheckStatus.NOT_WHITELISTED,
                    address=address,
                )

            if self.has_voted(address):
                return PrecheckResult(
                    status=PrecheckStatus.ALREADY_VOTED,
                    address=address,
                )

            balance = self.get_balance_wei(address)
            if balance < min_balance_wei:
                return PrecheckResult(
                    status=PrecheckStatus.INSUFFICIENT_BALANCE,
                    address=address,
                    balance_wei=balance,
                    required_wei=min_balance_wei,
                )

            return PrecheckResult(
                status=PrecheckStatus.OK,
                address=address,
                balance_wei=balance,
            )

        except Exception as exc:
            logger.warning("Precheck failed: %s", exc)
            return PrecheckResult(
                status=PrecheckStatus.UNKNOWN_ERROR,
                address=address,
                error_text=str(exc),
            )

    # ─────────────────────────────────────────────────────────────
    # Снимок статуса избирателя (для VoteTab)
    # ─────────────────────────────────────────────────────────────
    def get_voter_status(self, private_key: str) -> VoterStatus:
        """
        Возвращает снимок статуса избирателя.

        Делает все RPC-запросы здесь, в бизнес-слое.
        UI получает готовую структуру и не блокирует свой тред.

        Все опциональные поля могут быть None — UI обязан это учитывать.
        """
        if not self.validate_private_key(private_key):
            return VoterStatus(key_valid=False)

        try:
            address = self.get_address_from_key(private_key)
        except Exception as exc:
            return VoterStatus(
                key_valid=False,
                error=str(exc),
            )

        whitelisted: Optional[bool] = None
        voted: Optional[bool] = None
        balance: Optional[str] = None
        stage_name: Optional[str] = None

        try:
            whitelisted = self.is_whitelisted(address)
        except Exception:
            pass
        try:
            voted = self.has_voted(address)
        except Exception:
            pass
        try:
            balance = self.get_balance_eth(address)
        except Exception:
            pass
        try:
            stage = self.get_stage()
            stage_name = stage.name
        except Exception:
            pass

        return VoterStatus(
            key_valid=True,
            address=address,
            is_whitelisted=whitelisted,
            has_voted=voted,
            balance_eth=balance,
            stage_name=stage_name,
        )
    
    # ─────────────────────────────────────────────────────────────
    # API чтения
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
    # UI-фасад (изоляция от внутренних структур)
    # ─────────────────────────────────────────────────────────────
    def get_client_version(self) -> str:
        """Возвращает версию подключённого Geth-клиента."""
        return self.provider.client_version()

    def is_contract_deployed(self) -> bool:
        """True если контракт развёрнут в текущей сессии."""
        return bool(self.session.contract_address)

    def get_contract_address(self) -> Optional[str]:
        """Адрес развёрнутого контракта (или None)."""
        return self.session.contract_address

    def is_dev_mode(self) -> bool:
        """True если приложение запущено в dev-режиме."""
        return self.env.dev_mode

    def get_dev_admin_key(self) -> Optional[str]:
        """
        Возвращает admin-ключ из .env (только в dev-mode).
        В production-режиме возвращает None.
        """
        return self.env.dev_admin_key

    # ─────────────────────────────────────────────────────────────
    def _on_geth_crash(self) -> None:
        logger.critical("Geth node crashed")
        if self._crash_ui_callback:
            self._crash_ui_callback()