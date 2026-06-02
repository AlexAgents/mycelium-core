"""
Централизованное управление путями проекта.
Все пути вычисляются относительно корня проекта.

При запуске из PyInstaller EXE:
- BUNDLE_DIR: папка с распакованными ресурсами (_MEIxxxxx)
- ROOT: папка где лежит EXE (для bin/, data/, .env, app.cfg)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _find_project_root() -> Path:
    """
    Корень для внешних файлов (bin, data, .env, app.cfg).
    EXE: папка где лежит EXE.
    Исходники: папка с main.py.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "main.py").exists():
            return parent

    return Path(__file__).resolve().parent.parent.parent


def _find_bundle_dir() -> Path:
    """
    Корень для упакованных ресурсов (src/, contracts/).
    EXE: временная папка _MEIxxxxx (sys._MEIPASS).
    Исходники: то же что ROOT.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)

    return _find_project_root()


ROOT: Path = _find_project_root()
BUNDLE_DIR: Path = _find_bundle_dir()

# ── Внешние директории (рядом с EXE / в корне проекта) ──
DATA_DIR       : Path = ROOT / "data"
BIN_DIR        : Path = ROOT / "bin"

CHAIN_DIR      : Path = DATA_DIR / "chain-data"
CHAIN_ACTIVE   : Path = CHAIN_DIR / "active"
CHAIN_ARCHIVES : Path = CHAIN_DIR / "archives"

LOGS_DIR       : Path = DATA_DIR / "logs"
LOGS_ACTIVE    : Path = LOGS_DIR / "active"
LOGS_ARCHIVE   : Path = LOGS_DIR / "archive"

EXPORTS_DIR    : Path = DATA_DIR / "exports"
EXPORTS_VOTERS : Path = EXPORTS_DIR / "voters"
EXPORTS_RECEIPTS: Path = EXPORTS_DIR / "receipts"
EXPORTS_RESULTS : Path = EXPORTS_DIR / "results"

RUNTIME_DIR    : Path = DATA_DIR / "runtime"
RUNTIME_CACHE  : Path = RUNTIME_DIR / "cache"

# ── Конфигурационные файлы (рядом с EXE) ──
APP_CFG        : Path = ROOT / "app.cfg"
ENV_FILE       : Path = ROOT / ".env"
ENV_EXAMPLE    : Path = ROOT / ".env.example"

# ── Логи (внешние, data/) ──
SESSION_LOG    : Path = LOGS_ACTIVE / "session.log"

# ── Ресурсы (упакованы в EXE / в исходниках) ──
SRC_DIR        : Path = BUNDLE_DIR / "src"
CONTRACTS_DIR  : Path = BUNDLE_DIR / "contracts"
ABI_DIR        : Path = CONTRACTS_DIR / "abi"

UI_DIR         : Path = SRC_DIR / "ui"
THEMES_DIR     : Path = UI_DIR / "themes"
I18N_DIR       : Path = UI_DIR / "i18n"

# ── Файлы ресурсов ──
CONTRACT_SOL   : Path = CONTRACTS_DIR / "VotingCore.sol"
CONTRACT_ABI   : Path = ABI_DIR / "VotingCore.json"

# ── Бинарники (внешние, bin/) ──
import platform as _platform
_is_win = _platform.system() == "Windows"
GETH_BIN: Path = BIN_DIR / ("geth.exe" if _is_win else "geth")

# ── Genesis файл ──
GENESIS_FILE: Path = CHAIN_ACTIVE / "genesis.json"


def ensure_directories() -> None:
    """Создаёт все необходимые директории при первом запуске."""
    dirs = [
        DATA_DIR,
        BIN_DIR,
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

    # ABI директория — только если не frozen (в EXE она read-only)
    if not getattr(sys, 'frozen', False):
        CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
        ABI_DIR.mkdir(parents=True, exist_ok=True)


def get_archive_session_path(session_id: str) -> Path:
    """Возвращает путь для архива конкретной сессии."""
    return LOGS_ARCHIVE / session_id


def get_chain_archive_path(timestamp: str) -> Path:
    """Возвращает путь для архива chain-data."""
    return CHAIN_ARCHIVES / f"old_{timestamp}"