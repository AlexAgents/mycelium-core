"""
Управление конфигурацией приложения (app.cfg) и переменными окружения (.env).
"""

from __future__ import annotations

import configparser
import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

from src.utils.paths import APP_CFG, ENV_FILE, ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)

APP_VERSION = "0.0.1"

_DEFAULTS: dict[str, dict[str, str]] = {
    "app": {
        "version":  APP_VERSION,
        "language": "ru",
        "theme":    "dark",
    },
    "window": {
        "width":     "1280",
        "height":    "800",
        "x":         "100",
        "y":         "100",
        "maximized": "false",
    },
    "session": {
        "preferred_new_session_mode": "fast",
    },
    "paths": {
        "last_import_dir": "",
        "last_export_dir": "",
    },
    "dev": {
        "dev_mode": "false",
    },
}


class AppConfig:
    """
    Обёртка над configparser для чтения/записи app.cfg.
    Безопасна: не хранит приватные ключи.
    """

    def __init__(self) -> None:
        self._cfg = configparser.ConfigParser()
        self._load()

    # ─── Загрузка / сохранение ────────────────────────────────────────────

    def _load(self) -> None:
        """Загружает конфиг, создавая его при отсутствии."""
        if not APP_CFG.exists():
            logger.info("app.cfg not found — creating with defaults")
            self._apply_defaults()
            self._save()
            return

        self._cfg.read(APP_CFG, encoding="utf-8")
        saved_version = self._cfg.get("app", "version", fallback=None)

        if saved_version != APP_VERSION:
            logger.warning(
                "Config version mismatch: saved=%s current=%s — migrating",
                saved_version, APP_VERSION,
            )
            self._migrate(saved_version)

    def _apply_defaults(self) -> None:
        for section, values in _DEFAULTS.items():
            if not self._cfg.has_section(section):
                self._cfg.add_section(section)
            for key, value in values.items():
                if not self._cfg.has_option(section, key):
                    self._cfg.set(section, key, value)

    def _migrate(self, old_version: Optional[str]) -> None:
        """
        Создаёт резервную копию старого конфига и применяет дефолты
        для отсутствующих ключей, не затирая пользовательские настройки.
        """
        backup = APP_CFG.with_suffix(f".cfg.bak_{old_version or 'unknown'}")
        shutil.copy2(APP_CFG, backup)
        logger.info("Config backup saved: %s", backup)

        self._apply_defaults()
        self._cfg.set("app", "version", APP_VERSION)
        self._save()

    def _save(self) -> None:
        with open(APP_CFG, "w", encoding="utf-8") as f:
            self._cfg.write(f)

    def save(self) -> None:
        """Публичный метод сохранения."""
        self._save()
        logger.debug("app.cfg saved")

    # ─── Аксессоры ───────────────────────────────────────────────────────

    def get(self, section: str, key: str, fallback: Any = None) -> str:
        return self._cfg.get(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str) -> None:
        if not self._cfg.has_section(section):
            self._cfg.add_section(section)
        self._cfg.set(section, key, str(value))

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        return self._cfg.getboolean(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        return self._cfg.getint(section, key, fallback=fallback)

    # ─── Shortcuts ───────────────────────────────────────────────────────

    @property
    def language(self) -> str:
        return self.get("app", "language", fallback="ru")

    @language.setter
    def language(self, value: str) -> None:
        self.set("app", "language", value)

    @property
    def theme(self) -> str:
        return self.get("app", "theme", fallback="dark")

    @theme.setter
    def theme(self, value: str) -> None:
        self.set("app", "theme", value)

    @property
    def dev_mode(self) -> bool:
        return self.get_bool("dev", "dev_mode", fallback=False)

    @property
    def preferred_session_mode(self) -> str:
        return self.get("session", "preferred_new_session_mode", fallback="fast")

    @preferred_session_mode.setter
    def preferred_session_mode(self, value: str) -> None:
        self.set("session", "preferred_new_session_mode", value)


class EnvConfig:
    """
    Обёртка над переменными окружения из .env.
    Не используется как хранилище секретов в production.
    """

    def __init__(self) -> None:
        if ENV_FILE.exists():
            load_dotenv(ENV_FILE, override=False)
            logger.debug(".env loaded from %s", ENV_FILE)
        else:
            logger.debug(".env not found — using OS environment only")

    # ─── RPC ─────────────────────────────────────────────────────────────

    @property
    def rpc_host(self) -> str:
        return os.getenv("RPC_HOST", "127.0.0.1")

    @property
    def rpc_port(self) -> int:
        return int(os.getenv("RPC_PORT", "8545"))

    @property
    def rpc_url(self) -> str:
        return os.getenv("RPC_URL", f"http://{self.rpc_host}:{self.rpc_port}")

    # ─── Geth ────────────────────────────────────────────────────────────

    @property
    def network_id(self) -> int:
        return int(os.getenv("GETH_NETWORK_ID", "1337"))

    @property
    def gas_limit(self) -> int:
        return int(os.getenv("GETH_GAS_LIMIT", "8000000"))

    @property
    def gas_price(self) -> int:
        return int(os.getenv("DEFAULT_GAS_PRICE", "1000000000"))

    @property
    def default_gas(self) -> int:
        return int(os.getenv("DEFAULT_GAS", "500000"))

    # ─── Misc ────────────────────────────────────────────────────────────

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def dev_mode(self) -> bool:
        return os.getenv("DEV_MODE", "false").lower() == "true"

    @property
    def dev_admin_key(self) -> Optional[str]:
        """
        Возвращает admin key из .env ТОЛЬКО в dev mode.
        В production возвращает None.
        """
        if not self.dev_mode:
            return None
        return os.getenv("DEV_ADMIN_KEY")

    @property
    def solidity_version(self) -> str:
        return os.getenv("SOLIDITY_VERSION", "0.8.20")

    @property
    def expected_abi_hash(self) -> str:
        return os.getenv("EXPECTED_ABI_HASH", "")


# ─── Синглтоны ────────────────────────────────────────────────────────────────

_app_config: Optional[AppConfig] = None
_env_config: Optional[EnvConfig] = None


def get_app_config() -> AppConfig:
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config


def get_env_config() -> EnvConfig:
    global _env_config
    if _env_config is None:
        _env_config = EnvConfig()
    return _env_config