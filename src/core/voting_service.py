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
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.abi = abi
        self.contract = self.provider.get_contract(self.contract_address, abi)
        logger.info("Contract loaded: %s", self.contract_address)

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
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
            "gas": 3_000_000,
            "gasPrice": self.env.gas_price,
            "chainId": w3.eth.chain_id,
        })
        receipt = self._send_transaction(tx, admin_private_key)
        contract_address = receipt.contractAddress
        if not contract_address:
            raise RuntimeError("Deployment failed — no contract address")
        self.load_contract(contract_address, abi)
        logger.info("Contract deployed: %s", contract_address)
        admin_private_key = secure_clear(admin_private_key)
        return contract_address

    # ─────────────────────────────────────────────────────────────
    def add_candidate(self, admin_private_key: str, candidate: Candidate) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)
        tx = self.contract.functions.addCandidate(
            candidate.name,
            candidate.party,
            Web3.to_checksum_address(candidate.address),
        ).build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
            "gas": 500_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })
        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Candidate added: %s", candidate.address)
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    def add_voters_batch(self, admin_private_key: str, voters: list[str]) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)
        tx = self.contract.functions.addVotersBatch(
            [Web3.to_checksum_address(v) for v in voters]
        ).build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
            "gas": 3_000_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })
        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Whitelist batch added: %d voters", len(voters))
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    def start_voting(self, admin_private_key: str) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)
        tx = self.contract.functions.startVoting().build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
            "gas": 300_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })
        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Voting started")
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

    # ─────────────────────────────────────────────────────────────
    def finish_voting(self, admin_private_key: str) -> str:
        self._require_contract()
        account = Account.from_key(admin_private_key)
        tx = self.contract.functions.finishVoting().build_transaction({
            "from": account.address,
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
            "gas": 300_000,
            "gasPrice": self.env.gas_price,
            "chainId": self.provider.w3.eth.chain_id,
        })
        receipt = self._send_transaction(tx, admin_private_key)
        logger.info("Voting finished")
        admin_private_key = secure_clear(admin_private_key)
        return receipt.transactionHash.hex()

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
            "nonce": self._get_nonce_manager(account.address).get_next_nonce(),
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
    # READ API
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
        addresses = self.contract.functions.getCandidateAddresses().call()
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

    # ─────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────
    def _send_transaction(self, tx: dict, private_key: str):
        """
        Отправляет подписанную транзакцию.

        Политика retry:
        - ContractLogicError (revert): не повторяем, сразу поднимаем ошибку.
        - TimeExhausted: транзакция уже в сети, receipt просто не пришёл вовремя.
          FIX: НЕ повторяем с тем же nonce — это создало бы дубль.
          Синхронизируем nonce-менеджер и сообщаем пользователю.
        - ValueError (обычно "nonce too low"): синхронизируем nonce,
          пересобираем tx и повторяем не более 2 раз. (Проверить)
        """
        w3 = self.provider.w3
        retries = 2

        for attempt in range(retries + 1):
            try:
                signed = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                logger.info("Transaction broadcast: %s", tx_hash.hex())

                receipt = w3.eth.wait_for_transaction_receipt(
                    tx_hash, timeout=120, poll_latency=1,
                )
                if receipt.status != 1:
                    raise RuntimeError(f"Transaction reverted: {tx_hash.hex()}")
                logger.info("Transaction confirmed: %s", tx_hash.hex())
                return receipt

            except ContractLogicError as exc:
                logger.error("Contract revert: %s", exc)
                raise RuntimeError(
                    f"Smart contract rejected transaction:\n{exc}"
                ) from exc

            except TimeExhausted as exc:
                # FIX: транзакция была отправлена — не повторяем с тем же nonce.
                # Синхронизируем менеджер, чтобы следующий вызов получил
                # корректный nonce из сети.
                logger.error("Receipt timeout: %s", exc)
                self._get_nonce_manager(tx["from"]).sync()
                raise RuntimeError(
                    "Transaction confirmation timeout. "
                    "The transaction may still be pending — "
                    "check the blockchain before retrying."
                ) from exc

            except ValueError as exc:
                # Обычно: nonce too low / already known.
                # FIX: синхронизируем nonce, пересобираем tx и повторяем.
                logger.exception("RPC transaction error: %s", exc)
                nm = self._get_nonce_manager(tx["from"])
                nm.sync()
                if attempt < retries:
                    tx["nonce"] = nm.get_next_nonce()
                    logger.warning(
                        "Nonce re-synced, retrying (attempt %d/%d)...",
                        attempt + 1, retries,
                    )
                    time.sleep(1)
                    continue
                raise RuntimeError(f"RPC error:\n{exc}") from exc

            except Exception as exc:
                logger.exception("Unexpected transaction failure")
                raise RuntimeError(
                    f"Blockchain transaction failed:\n{exc}"
                ) from exc

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