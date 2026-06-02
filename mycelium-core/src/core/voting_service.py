"""
VotingService.

Инкапсулирует ВСЮ blockchain-логику.
UI не должен работать с Web3 напрямую.
"""
from __future__ import annotations

import time
from typing import Optional

from eth_account import Account
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError, TimeExhausted

from src.core.models import Candidate, ElectionStage, VoteReceipt
from src.core.nonce_manager import NonceManager
from src.core.web3_provider import Web3Provider
from src.utils.config import get_env_config
from src.utils.crypto import secure_clear
from src.utils.logger import get_logger
from src.utils.qr import generate_receipt_qr

logger = get_logger(__name__)

# Известные паттерны ошибок Geth
_ERR_INSUFFICIENT_FUNDS = "insufficient funds"
_ERR_NONCE_TOO_LOW = "nonce too low"
_ERR_ALREADY_KNOWN = "already known"
_ERR_NOT_WHITELISTED = "NotWhitelisted"
_ERR_ALREADY_VOTED = "AlreadyVoted"
_ERR_CANDIDATE_NOT_FOUND = "CandidateNotFound"
_ERR_INVALID_STAGE = "InvalidStage"
_ERR_UNAUTHORIZED = "Unauthorized"


class VotingService:
    def __init__(self, provider: Web3Provider) -> None:
        self.provider = provider
        self.env = get_env_config()

        self.contract: Optional[Contract] = None
        self.contract_address: Optional[str] = None
        self.abi: Optional[list] = None
        self.bytecode: Optional[str] = None

        self._nonce_managers: dict[str, NonceManager] = {}

    # ─────────────────────────────────────────────────────────────
    def load_contract(self, contract_address: str, abi: list) -> None:
        self.contract_address = Web3.to_checksum_address(
            contract_address
        )
        self.abi = abi
        self.contract = self.provider.get_contract(
            self.contract_address, abi
        )
        logger.info("Contract loaded: %s", self.contract_address)

    # ─────────────────────────────────────────────────────────────
    def reset(self) -> None:
        """Сбрасывает состояние для новой сессии."""
        self.contract = None
        self.contract_address = None
        self.abi = None
        self.bytecode = None
        self._nonce_managers.clear()
        logger.info("VotingService reset")

    # ─────────────────────────────────────────────────────────────
    # Деплой
    # ─────────────────────────────────────────────────────────────
    def deploy_contract(
        self,
        admin_private_key: str,
        abi: list,
        bytecode: str,
    ) -> str:
        w3 = self.provider.w3
        account = Account.from_key(admin_private_key)
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        tx = contract.constructor().build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(
                account.address
            ).get_next_nonce(),
            "gas": 3_000_000,
            "gasPrice": self.env.gas_price,
            "chainId": w3.eth.chain_id,
        })

        receipt = self._send_transaction(tx, admin_private_key)
        contract_address = receipt.contractAddress

        if not contract_address:
            raise RuntimeError(
                "Deployment failed: no contract address in receipt"
            )

        self.load_contract(contract_address, abi)
        logger.info("Contract deployed: %s", contract_address)

        admin_private_key = secure_clear(admin_private_key)
        return contract_address

    # ─────────────────────────────────────────────────────────────
    # Перевод ETH
    # ─────────────────────────────────────────────────────────────
    def fund_account(
        self,
        sender_private_key: str,
        target_address: str,
        amount_wei: int,
    ) -> str:
        """Переводит ETH. Не требует контракта."""
        w3 = self.provider.w3
        account = Account.from_key(sender_private_key)

        tx = {
            "from": account.address,
            "to": Web3.to_checksum_address(target_address),
            "value": amount_wei,
            "nonce": self._get_nonce_manager(
                account.address
            ).get_next_nonce(),
            "gas": 21_000,
            "gasPrice": self.env.gas_price,
            "chainId": w3.eth.chain_id,
        }

        receipt = self._send_transaction(tx, sender_private_key)
        tx_hash = receipt.transactionHash.hex()

        logger.info(
            "Funded %s with %d wei, tx=%s",
            target_address[:10], amount_wei, tx_hash[:16],
        )
        sender_private_key = secure_clear(sender_private_key)
        return tx_hash

    # ─────────────────────────────────────────────────────────────
    # Управление кандидатами
    # ─────────────────────────────────────────────────────────────
    def add_candidate(
        self, admin_private_key: str, candidate: Candidate
    ) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)

        tx = self.contract.functions.addCandidate(
            candidate.name,
            candidate.party,
            Web3.to_checksum_address(candidate.address),
        ).build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(
                account.address
            ).get_next_nonce(),
            "gas": 500_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })

        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Candidate added: %s", candidate.address)
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    # Whitelist (белый список)
    # ─────────────────────────────────────────────────────────────
    def add_voters_batch(
        self, admin_private_key: str, voters: list[str]
    ) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)

        tx = self.contract.functions.addVotersBatch(
            [Web3.to_checksum_address(v) for v in voters]
        ).build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(
                account.address
            ).get_next_nonce(),
            "gas": 3_000_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })

        receipt = self._send_transaction(tx, admin_private_key)
        logger.info(
            "Whitelist batch: %d voters", len(voters)
        )
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    # Управление стадиями
    # ─────────────────────────────────────────────────────────────
    def start_voting(self, admin_private_key: str) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)

        tx = self.contract.functions.startVoting().build_transaction(
            {
                "from": account.address,
                "nonce": self._get_nonce_manager(
                    account.address
                ).get_next_nonce(),
                "gas": 300_000,
                "gasPrice": self.env.gas_price,
                "chainId": self.provider.w3.eth.chain_id,
            }
        )

        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Voting started")
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    def finish_voting(self, admin_private_key: str) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)

        tx = self.contract.functions.finishVoting().build_transaction(
            {
                "from": account.address,
                "nonce": self._get_nonce_manager(
                    account.address
                ).get_next_nonce(),
                "gas": 300_000,
                "gasPrice": self.env.gas_price,
                "chainId": self.provider.w3.eth.chain_id,
            }
        )

        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Voting finished")
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    # Голосование
    # ─────────────────────────────────────────────────────────────
    def cast_vote(
        self,
        voter_private_key: str,
        candidate_address: str,
        session_id: str,
    ) -> VoteReceipt:
        self._require_contract()
        account = Account.from_key(voter_private_key)

        tx = self.contract.functions.castVote(
            Web3.to_checksum_address(candidate_address)
        ).build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(
                account.address
            ).get_next_nonce(),
            "gas": 300_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })

        receipt = self._send_transaction(tx, voter_private_key)
        tx_hash = receipt.transactionHash.hex()

        qr = generate_receipt_qr(
            tx_hash=tx_hash,
            voter_address=account.address,
            candidate_address=candidate_address,
            block_number=receipt.blockNumber,
            session_id=session_id,
        )

        vote_receipt = VoteReceipt(
            tx_hash=tx_hash,
            voter_address=account.address,
            candidate_address=candidate_address,
            block_number=receipt.blockNumber,
            session_id=session_id,
            qr_bytes=qr,
        )

        logger.info(
            "Vote cast: voter=%s candidate=%s tx=%s",
            account.address, candidate_address, tx_hash,
        )
        voter_private_key = secure_clear(voter_private_key)
        return vote_receipt

    # ─────────────────────────────────────────────────────────────
    # API чтения
    # ─────────────────────────────────────────────────────────────
    def get_stage(self) -> ElectionStage:
        self._require_contract()
        stage = self.contract.functions.currentStage().call()
        return ElectionStage(stage)

    def has_voted(self, address: str) -> bool:
        self._require_contract()
        return self.contract.functions.hasVoted(
            Web3.to_checksum_address(address)
        ).call()

    def is_whitelisted(self, address: str) -> bool:
        self._require_contract()
        return self.contract.functions.whitelist(
            Web3.to_checksum_address(address)
        ).call()

    def get_candidates(self) -> list[Candidate]:
        self._require_contract()
        result: list[Candidate] = []
        addresses = (
            self.contract.functions.getCandidateAddresses().call()
        )
        for addr in addresses:
            data = self.contract.functions.getCandidate(addr).call()
            result.append(Candidate(
                name=data[0],
                party=data[1],
                address=addr,
                vote_count=data[3],
                registered=data[2],
            ))
        return result

    def get_owner(self) -> str:
        """Возвращает адрес owner'а контракта."""
        self._require_contract()
        return self.contract.functions.owner().call()

    # ─────────────────────────────────────────────────────────────
    # Внутренний: отправка транзакций (с retry)
    # ─────────────────────────────────────────────────────────────
    def _send_transaction(self, tx: dict, private_key: str):
        """
        Отправляет подписанную транзакцию.

        Улучшенная политика retry:
        - ContractLogicError: парсим revert reason, НЕ повторяем.
        - TimeExhausted: sync nonce, НЕ повторяем (TX уже в сети).
        - ValueError (nonce too low / already known):
          sync nonce + rebuild tx, до 3 попыток с backoff.
        - Web3RPCError (insufficient funds и др.):
          парсим, поднимаем понятную ошибку.
        """
        w3 = self.provider.w3
        max_retries = 3

        for attempt in range(max_retries + 1):
            try:
                signed = w3.eth.account.sign_transaction(
                    tx, private_key
                )
                tx_hash = w3.eth.send_raw_transaction(
                    signed.raw_transaction
                )
                logger.info(
                    "TX broadcast: %s (attempt %d)",
                    tx_hash.hex(), attempt + 1,
                )

                receipt = w3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=120, poll_latency=1,
                )

                if receipt.status != 1:
                    raise RuntimeError(
                        f"Transaction reverted: {tx_hash.hex()}"
                    )

                logger.info("TX confirmed: %s", tx_hash.hex())
                return receipt

            except ContractLogicError as exc:
                logger.error("Contract revert: %s", exc)
                raise RuntimeError(
                    self._humanize_contract_error(str(exc))
                ) from exc

            except TimeExhausted as exc:
                logger.error("Receipt timeout: %s", exc)
                self._get_nonce_manager(tx["from"]).sync()
                raise RuntimeError(
                    "Transaction confirmation timeout.\n"
                    "The TX may still be pending in the mempool."
                ) from exc

            except ValueError as exc:
                error_str = str(exc).lower()
                logger.warning(
                    "TX ValueError (attempt %d/%d): %s",
                    attempt + 1, max_retries, exc,
                )

                # Недостаточно средств — не повторяем
                if _ERR_INSUFFICIENT_FUNDS in error_str:
                    self._get_nonce_manager(tx["from"]).sync()
                    raise RuntimeError(
                        "Insufficient funds for gas.\n"
                        "The sender account does not have "
                        "enough ETH to pay for this transaction."
                    ) from exc

                # Ошибки nonce — повторяем
                if (
                    _ERR_NONCE_TOO_LOW in error_str
                    or _ERR_ALREADY_KNOWN in error_str
                ):
                    nm = self._get_nonce_manager(tx["from"])
                    nm.sync()

                    if attempt < max_retries:
                        tx["nonce"] = nm.get_next_nonce()
                        backoff = min(2 ** attempt, 8)
                        logger.info(
                            "Nonce re-synced, retry in %ds",
                            backoff,
                        )
                        time.sleep(backoff)
                        continue

                    raise RuntimeError(
                        "Nonce conflict persists after "
                        f"{max_retries} retries.\n"
                        "Try again or restart the session."
                    ) from exc

                # Неизвестная ValueError
                raise RuntimeError(
                    f"RPC error:\n{exc}"
                ) from exc

            except Exception as exc:
                error_str = str(exc).lower()

                # Ловим Web3RPCError (insufficient funds и др.)
                if _ERR_INSUFFICIENT_FUNDS in error_str:
                    self._get_nonce_manager(tx["from"]).sync()
                    raise RuntimeError(
                        "Insufficient funds for gas.\n"
                        "The sender account does not have "
                        "enough ETH to pay for this transaction.\n"
                        "Use 'Fund Voters' or check admin balance."
                    ) from exc

                logger.exception("Unexpected TX failure")
                raise RuntimeError(
                    f"Blockchain transaction failed:\n{exc}"
                ) from exc

        # Сюда не должны попасть
        raise RuntimeError("Transaction failed after all retries")

    # ─────────────────────────────────────────────────────────────
    def _humanize_contract_error(self, error_text: str) -> str:
        """Преобразует revert reason в понятное сообщение."""
        mapping = {
            _ERR_NOT_WHITELISTED: (
                "This address is not in the whitelist.\n"
                "Only whitelisted voters can cast votes."
            ),
            _ERR_ALREADY_VOTED: (
                "This address has already voted.\n"
                "Each voter can only vote once."
            ),
            _ERR_CANDIDATE_NOT_FOUND: (
                "The selected candidate is not registered.\n"
                "Vote can only be cast for registered candidates."
            ),
            _ERR_INVALID_STAGE: (
                "Operation not allowed at the current stage.\n"
                "Check that voting is in the correct phase."
            ),
            _ERR_UNAUTHORIZED: (
                "Only the contract owner can perform "
                "this action."
            ),
        }

        for pattern, message in mapping.items():
            if pattern in error_text:
                return message

        return f"Smart contract rejected the transaction:\n{error_text}"

    # ─────────────────────────────────────────────────────────────
    def _get_nonce_manager(self, address: str) -> NonceManager:
        checksum = Web3.to_checksum_address(address)
        if checksum not in self._nonce_managers:
            self._nonce_managers[checksum] = NonceManager(
                self.provider.w3, checksum
            )
        return self._nonce_managers[checksum]

    # ─────────────────────────────────────────────────────────────
    def _require_contract(self) -> None:
        if self.contract is None:
            raise RuntimeError("Contract not loaded")