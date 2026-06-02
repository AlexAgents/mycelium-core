"""
Централизованное логирование MYCELIUM CORE.
Запрещено логировать приватные ключи и любые секреты.
"""

from __future__ import annotations
import re
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


from src.utils.paths import (
    LOGS_ACTIVE,
    SESSION_LOG,
    get_archive_session_path,
)

_PRIVATE_KEY_RE = re.compile(r"0x[a-fA-F0-9]{64}")

_SENTINEL_PATTERNS = (
    "private_key",
    "privkey",
    "priv_key",
    "secret",
    "mnemonic",
    "seed",
    "0x" + "a" * 62,  # шаблон — в реальном коде проверяем длину
)

class _SecretFilter(logging.Filter):
    """
    Предотвращает утечку секретов в лог.
    """

    BLOCKED_KEYWORDS = (
        "private_key",
        "privkey",
        "priv_key",
        "mnemonic",
        "seed phrase",
        "secret",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.getMessage())

        lowered = msg.lower()

        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in lowered:
                record.msg = "[REDACTED — secret suppressed]"
                record.args = ()
                return True

        if _PRIVATE_KEY_RE.search(msg):
            record.msg = "[REDACTED — private key pattern suppressed]"
            record.args = ()
            return True

        return True

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _build_handler(log_path: Path) -> logging.FileHandler:
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(_formatter)
    handler.addFilter(_SecretFilter())
    return handler


def _build_console_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)
    handler.addFilter(_SecretFilter())
    return handler


# Глобальный файловый обработчик — сменяется при архивации
_file_handler: Optional[logging.FileHandler] = None


def setup_logging(level: str = "INFO") -> None:
    """
    Инициализирует систему логирования.
    Вызывается один раз при старте приложения.
    """
    global _file_handler

    LOGS_ACTIVE.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Убираем дубликаты при повторном вызове
    root_logger.handlers.clear()

    _file_handler = _build_handler(SESSION_LOG)
    root_logger.addHandler(_file_handler)
    root_logger.addHandler(_build_console_handler())

    root_logger.info("=" * 70)
    root_logger.info("MYCELIUM CORE — logging initialized (level=%s)", level)
    root_logger.info("Log file: %s", SESSION_LOG)
    root_logger.info("=" * 70)


def archive_session_log(session_id: str) -> Optional[Path]:
    """
    Архивирует текущий лог сессии в logs/archive/<session_id>/.
    Возвращает путь к архивному файлу или None при ошибке.
    """
    global _file_handler

    if not SESSION_LOG.exists():
        return None

    archive_dir = get_archive_session_path(session_id)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / "session.log"

    # Закрываем файловый обработчик перед копированием
    logger = logging.getLogger(__name__)
    root_logger = logging.getLogger()

    if _file_handler:
        _file_handler.close()
        root_logger.removeHandler(_file_handler)
        _file_handler = None

    try:
        shutil.copy2(SESSION_LOG, archive_path)
        # Очищаем активный лог
        SESSION_LOG.write_text("", encoding="utf-8")
        logger.info("Log archived to: %s", archive_path)

        # Переподключаем файловый обработчик
        _file_handler = _build_handler(SESSION_LOG)
        root_logger.addHandler(_file_handler)

        return archive_path
    except OSError as exc:
        logger.error("Failed to archive log: %s", exc)
        # Восстанавливаем обработчик
        _file_handler = _build_handler(SESSION_LOG)
        root_logger.addHandler(_file_handler)
        return None


def get_logger(name: str) -> logging.Logger:
    """Возвращает именованный логгер для модуля."""
    return logging.getLogger(name)