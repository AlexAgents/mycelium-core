"""
Криптографические утилиты.
Не хранит ключи — только вычисляет производные значения.
"""

from __future__ import annotations

import secrets
from typing import Tuple

from eth_account import Account

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Включаем поддержку HD-кошельков (не используем, но пакет требует явного флага)
Account.enable_unaudited_hdwallet_features()


def generate_eth_keypair() -> Tuple[str, str]:
    """
    Генерирует новую пару (приватный ключ, адрес).
    Возвращает (private_key_hex, address).
    Не логирует приватный ключ.
    """
    account = Account.create(secrets.token_bytes(32))
    priv_key = account.key.hex()          # 0x-prefixed hex строка
    address  = account.address            # checksum адрес
    logger.debug("Generated new keypair — address: %s", address)
    return priv_key, address


def address_from_private_key(private_key: str) -> str:
    """
    Вычисляет Ethereum-адрес из приватного ключа.
    Не логирует ключ.
    Raises ValueError если ключ невалиден.
    """
    try:
        account = Account.from_key(private_key)
        return account.address
    except Exception as exc:
        raise ValueError(f"Invalid private key: {exc}") from exc


def generate_test_voters(count: int) -> list[dict]:
    """
    Генерирует список тестовых избирателей.
    Возвращает список словарей {"address": ..., "private_key": ...}.
    """
    voters = []
    for _ in range(count):
        priv, addr = generate_eth_keypair()
        voters.append({
            "address":     addr,
            "private_key": priv,
            "has_voted":   False,
        })
    logger.info("Generated %d test voter keypairs", count)
    return voters


def secure_clear(key_str: str) -> str:
    """
    Best-effort очистка строки с секретом.

    В CPython невозможно гарантированно очистить память
    immutable string-объектов, но функция пытается
    минимизировать время жизни копий ключа в памяти.
    """
    # Перезаписываем содержимое нулями в bytearray (best effort)
    try:
        key_bytes = bytearray(key_str.encode("utf-8"))
        for i in range(len(key_bytes)):
            key_bytes[i] = 0
    except Exception:
        pass
    return ""