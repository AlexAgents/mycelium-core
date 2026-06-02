"""
Web3 provider.
Единственная точка подключения к Ethereum RPC.
UI не должен использовать Web3 напрямую.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Optional

from web3 import Web3

from src.utils.logger import get_logger

logger = get_logger(__name__)

RPC_WAIT_TIMEOUT_SEC = 30
RPC_POLL_INTERVAL_SEC = 0.5


def _inject_poa_middleware(w3: Web3) -> None:
    """
    FIX: geth_poa_middleware переименован в ExtraDataToPOAMiddleware
    в web3.py 6.x. Поддерживаем обе версии.
    """
    try:
        # web3 >= 6.0
        from web3.middleware import ExtraDataToPOAMiddleware  # type: ignore
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        logger.debug("POA middleware: ExtraDataToPOAMiddleware (web3 v6+)")
    except ImportError:
        # web3 < 6.0
        from web3.middleware import geth_poa_middleware  # type: ignore
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        logger.debug("POA middleware: geth_poa_middleware (web3 v5)")


class Web3Provider:
    def __init__(self, rpc_url: str) -> None:
        self.rpc_url = rpc_url
        self._w3: Optional[Web3] = None

    # ─────────────────────────────────────────────────────────────
    # Connection
    # ─────────────────────────────────────────────────────────────
    def connect(self) -> None:
        self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        _inject_poa_middleware(self._w3)
        logger.info("Web3 connected: %s", self.rpc_url)

    def wait_for_rpc(self, timeout: int = RPC_WAIT_TIMEOUT_SEC) -> bool:
        if self._w3 is None:
            self.connect()
        deadline = time.monotonic() + timeout
        attempts = 0
        while time.monotonic() < deadline:
            try:
                if self._w3.is_connected():
                    block = self._w3.eth.block_number
                    logger.info("RPC ready block=%d", block)
                    return True
            except Exception:
                pass
            attempts += 1
            time.sleep(RPC_POLL_INTERVAL_SEC)
        logger.error("RPC unavailable after %d attempts", attempts)
        return False

    def is_connected(self) -> bool:
        if self._w3 is None:
            return False
        try:
            return self._w3.is_connected()
        except Exception:
            return False

    # ─────────────────────────────────────────────────────────────
    # Diagnostics
    # ─────────────────────────────────────────────────────────────
    def ping(self) -> bool:
        """
        FIX: использует self._w3 напрямую вместо self.w3 (property с raise),
        чтобы не бросать RuntimeError при вызове до connect().
        """
        if self._w3 is None:
            return False
        try:
            self._w3.eth.block_number
            return True
        except Exception:
            return False

    def client_version(self) -> str:
        """
        FIX: безопасная версия — не кидает RuntimeError если не подключены.
        """
        if self._w3 is None:
            return "unknown"
        try:
            return self._w3.client_version
        except Exception:
            return "unknown"

    # ─────────────────────────────────────────────────────────────
    # Blockchain info
    # ─────────────────────────────────────────────────────────────
    def get_block_number(self) -> Optional[int]:
        try:
            return self.w3.eth.block_number
        except Exception as exc:
            logger.debug("Block query failed: %s", exc)
            return None

    def get_chain_id(self) -> int:
        return self.w3.eth.chain_id

    # ─────────────────────────────────────────────────────────────
    # Accounts
    # ─────────────────────────────────────────────────────────────
    def get_accounts(self) -> list[str]:
        try:
            return list(self.w3.eth.accounts)
        except Exception:
            return []

    def get_balance(self, address: str) -> int:
        try:
            return self.w3.eth.get_balance(
                Web3.to_checksum_address(address)
            )
        except Exception:
            return 0

    # ─────────────────────────────────────────────────────────────
    # Contracts
    # ─────────────────────────────────────────────────────────────
    def get_contract(self, address: str, abi: list):
        checksum = Web3.to_checksum_address(address)
        return self.w3.eth.contract(address=checksum, abi=abi)

    # ─────────────────────────────────────────────────────────────
    # ABI validation
    # ─────────────────────────────────────────────────────────────
    def validate_abi_hash(self, abi: list, expected_hash: str) -> bool:
        if not expected_hash:
            return True
        abi_json = json.dumps(abi, sort_keys=True, separators=(",", ":"))
        actual_hash = hashlib.sha256(abi_json.encode()).hexdigest()
        if actual_hash != expected_hash:
            logger.warning("ABI hash mismatch")
            return False
        return True

    # ─────────────────────────────────────────────────────────────
    # Raw access (требует подключения)
    # ─────────────────────────────────────────────────────────────
    @property
    def w3(self) -> Web3:
        if self._w3 is None:
            raise RuntimeError("Web3Provider not connected")
        return self._w3