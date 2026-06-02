"""
Централизованный менеджер nonce.
Предотвращает конфликты транзакций при пакетных операциях.
"""

from __future__ import annotations

import threading
from typing import Optional
from web3 import Web3
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NonceManager:
    """
    Thread-safe менеджер nonce для одного аккаунта.
    Все write-операции в системе должны получать nonce через этот класс.
    """

    def __init__(self, w3: Web3, address: str) -> None:
        self._w3      = w3
        self._address = Web3.to_checksum_address(address)
        self._lock    = threading.Lock()
        self._nonce:  Optional[int] = None

    # ─── Публичный API ─────────────────────────────────────────────
    def get_next_nonce(self) -> int:
        """
        Возвращает следующий доступный nonce.

        Инвариант: self._nonce всегда хранит СЛЕДУЮЩИЙ доступный nonce,
        а не последний выданный. Возвращаем его и сразу инкрементируем,
        чтобы избежать off-by-one после sync().
        """
        with self._lock:
            if self._nonce is None:
                self._nonce = self._fetch_network_nonce()
                logger.debug(
                    "Nonce initialized for %s: %d",
                    self._address, self._nonce,
                )
            issued = self._nonce
            self._nonce += 1
            logger.debug(
                "Nonce %d issued for %s", issued, self._address,
            )
            return issued

    def sync(self) -> None:
        """
        Принудительно синхронизирует nonce с сетью.
        Вызывать после ошибок транзакций.

        После sync() следующий get_next_nonce() вернёт ровно то значение,
        которое сеть считает pending — без пропуска.
        """
        with self._lock:
            old = self._nonce
            self._nonce = self._fetch_network_nonce()
            logger.info(
                "Nonce re-synced for %s: %s -> %d (next available)",
                self._address, old, self._nonce,
            )

    def reset(self) -> None:
        """Сбрасывает состояние (при смене аккаунта / новой сессии)."""
        with self._lock:
            self._nonce = None
            logger.debug("NonceManager reset for %s", self._address)

    # ─── Внутренние методы ──────────────────────────────────────────
    def _fetch_network_nonce(self) -> int:
        return self._w3.eth.get_transaction_count(
            self._address, block_identifier="pending"
        )