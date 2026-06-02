"""
Централизованное управление путями проекта.
Все пути вычисляются относительно корня проекта.
"""

from __future__ import annotations

import os
from pathlib import Path


def _find_project_root() -> Path:
    """
    Находит корневую папку проекта по наличию main.py.
    Работает независимо от того, откуда запущено приложение.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "main.py").exists():
            return parent
    # Запасной вариант — три уровня вверх от utils/
    return Path(__file__).resolve().parent.parent.parent


ROOT: Path = _find_project_root()

# Основные директории

BIN_DIR        : Path = ROOT / "bin"
CONTRACTS_DIR  : Path = ROOT / "contracts"
ABI_DIR        : Path = CONTRACTS_DIR / "abi"
SRC_DIR        : Path = ROOT / "src"
CHAIN_DIR      : Path = ROOT / "chain-data"
CHAIN_ACTIVE   : Path = CHAIN_DIR / "active"
CHAIN_ARCHIVES : Path = CHAIN_DIR / "archives"
LOGS_DIR       : Path = ROOT / "logs"
LOGS_ACTIVE    : Path = LOGS_DIR / "active"
LOGS_ARCHIVE   : Path = LOGS_DIR / "archive"
EXPORTS_DIR    : Path = ROOT / "exports"
EXPORTS_VOTERS : Path = EXPORTS_DIR / "voters"
EXPORTS_RECEIPTS: Path = EXPORTS_DIR / "receipts"
EXPORTS_RESULTS : Path = EXPORTS_DIR / "results"
RUNTIME_DIR    : Path = ROOT / "runtime"
RUNTIME_CACHE  : Path = RUNTIME_DIR / "cache"
UI_DIR         : Path = SRC_DIR / "ui"
THEMES_DIR     : Path = UI_DIR / "themes"
I18N_DIR       : Path = UI_DIR / "i18n"

# Файлы

APP_CFG        : Path = ROOT / "app.cfg"
ENV_FILE       : Path = ROOT / ".env"
ENV_EXAMPLE    : Path = ROOT / ".env.example"
SESSION_LOG    : Path = LOGS_ACTIVE / "session.log"
CONTRACT_SOL   : Path = CONTRACTS_DIR / "VotingCore.sol"
CONTRACT_ABI   : Path = ABI_DIR / "VotingCore.json"

# Бинарники

import platform as _platform

_is_win = _platform.system() == "Windows"
GETH_BIN: Path = BIN_DIR / ("geth.exe" if _is_win else "geth")
SOLC_BIN: Path = BIN_DIR / ("solc.exe" if _is_win else "solc")

# Genesis файл

GENESIS_FILE: Path = CHAIN_ACTIVE / "genesis.json"


def ensure_directories() -> None:
    """Создаёт все необходимые директории при первом запуске."""
    dirs = [
        BIN_DIR,
        CONTRACTS_DIR,
        ABI_DIR,
        CHAIN_DIR,
        CHAIN_ACTIVE,
        CHAIN_ARCHIVES,
        LOGS_DIR,
        LOGS_ACTIVE,
        LOGS_ARCHIVE,
        EXPORTS_DIR,
        EXPORTS_VOTERS,
        EXPORTS_RECEIPTS,
        EXPORTS_RESULTS,
        RUNTIME_DIR,
        RUNTIME_CACHE,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def get_archive_session_path(session_id: str) -> Path:
    """Возвращает путь для архива конкретной сессии."""
    return LOGS_ARCHIVE / session_id


def get_chain_archive_path(timestamp: str) -> Path:
    """Возвращает путь для архива chain-data."""
    return CHAIN_ARCHIVES / f"old_{timestamp}"