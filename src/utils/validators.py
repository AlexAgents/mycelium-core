"""
Валидаторы входных данных.
"""

from __future__ import annotations

import re
from typing import Tuple

from eth_account import Account
from web3 import Web3

_ETH_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
_PRIV_KEY_RE = re.compile(r"^(0x)?[0-9a-fA-F]{64}$")


def is_valid_eth_address(value: str) -> bool:
    """
    Проверяет Ethereum-адрес:
    - формат
    - checksum/base validity через Web3
    """

    if not isinstance(value, str):
        return False

    value = value.strip()

    if not _ETH_ADDR_RE.match(value):
        return False

    try:
        return Web3.is_address(value)
    except Exception:
        return False


def is_valid_private_key(value: str) -> bool:
    """
    Проверяет приватный ключ:
    - regex
    - возможность derivation account
    """

    if not isinstance(value, str):
        return False

    value = value.strip()

    if not _PRIV_KEY_RE.match(value):
        return False

    try:
        Account.from_key(normalize_private_key(value))
        return True
    except Exception:
        return False


def normalize_private_key(value: str) -> str:
    """Нормализует приватный ключ."""

    value = value.strip()

    if not value.startswith("0x"):
        value = "0x" + value

    return value.lower()


def validate_candidate_name(name: str) -> Tuple[bool, str]:
    name = name.strip()

    if not name:
        return False, "Candidate name cannot be empty"

    if len(name) > 100:
        return False, "Candidate name too long"

    return True, ""


def validate_candidate_party(party: str) -> Tuple[bool, str]:
    party = party.strip()

    if not party:
        return False, "Party cannot be empty"

    if len(party) > 100:
        return False, "Party name too long"

    return True, ""


def validate_candidate_limit(count: int) -> Tuple[bool, str]:
    if count < 2:
        return False, "Minimum 2 candidates required"

    if count > 10:
        return False, "Maximum 10 candidates allowed"

    return True, ""

def validate_voter_count(
    count: int,
) -> Tuple[bool, str]:

    if count < 1:
        return False, "Minimum count is 1"

    if count > 1000:
        return False, "Maximum count is 1000"

    return True, ""