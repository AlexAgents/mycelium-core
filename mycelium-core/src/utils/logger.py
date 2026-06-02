"""
Централизованное логирование MYCELIUM CORE.

Запрещено логировать приватные ключи и любые секреты.

При старте автоматически архивирует session.log от прошлого запуска
в logs/archive/<timestamp>_startup/, чтобы текущая сессия начиналась
с чистого файла.
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
    LOGS_ARCHIVE,
    SESSION_LOG,
    get_archive_session_path,
)


_PRIVATE_KEY_RE = re.compile(r"0x[a-fA-F0-9]{64}")


class _SecretFilter(logging.Filter):
    """Предотвращает утечку секретов в лог."""

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


def _archive_previous_log() -> None:
    """
    Архивирует session.log от прошлого запуска при старте приложения.

    Создаёт папку logs/archive/<timestamp>_startup/ и копирует туда
    оставшийся session.log, после чего очищает рабочий файл.

    Не падает если архивация не удалась — просто молча продолжает.
    """
    if not SESSION_LOG.exists():
        return
    try:
        size = SESSION_LOG.stat().st_size
        if size == 0:
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_startup")
        archive_dir = LOGS_ARCHIVE / ts
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SESSION_LOG, archive_dir / "session.log")
        SESSION_LOG.write_text("", encoding="utf-8")
    except Exception:
        # Архивация при старте — best-effort, ошибка не критична
        pass


# Глобальный файловый обработчик — сменяется при архивации
_file_handler: Optional[logging.FileHandler] = None


def setup_logging(level: str = "INFO") -> None:
    """
    Инициализирует систему логирования.

    Вызывается один раз при старте приложения.

    При старте:
        1. Создаёт нужные директории.
        2. Архивирует session.log от прошлого запуска (если есть).
        3. Настраивает root logger.
    """
    global _file_handler

    LOGS_ACTIVE.mkdir(parents=True, exist_ok=True)
    LOGS_ARCHIVE.mkdir(parents=True, exist_ok=True)

    # Архивируем оставшийся лог от прошлого запуска
    _archive_previous_log()

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()

    _file_handler = _build_handler(SESSION_LOG)
    root_logger.addHandler(_file_handler)
    root_logger.addHandler(_build_console_handler())

    root_logger.info("=" * 70)
    root_logger.info(
        "MYCELIUM CORE — logging initialized (level=%s)", level
    )
    root_logger.info("Log file: %s", SESSION_LOG)
    root_logger.info("=" * 70)


def archive_session_log(session_id: str) -> Optional[Path]:
    """
    Архивирует текущий лог сессии в logs/archive/<session_id>/.

    Используется при new_session и при shutdown.

    Returns:
        Path к архивному файлу, или None при ошибке.
    """
    global _file_handler

    if not SESSION_LOG.exists():
        return None

    archive_dir = get_archive_session_path(session_id)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / "session.log"

    logger = logging.getLogger(__name__)
    root_logger = logging.getLogger()

    # Закрыть файловый handler перед копированием
    if _file_handler:
        _file_handler.close()
        root_logger.removeHandler(_file_handler)
        _file_handler = None

    try:
        shutil.copy2(SESSION_LOG, archive_path)
        # Очистить активный лог
        SESSION_LOG.write_text("", encoding="utf-8")
        logger.info("Log archived to: %s", archive_path)

        # Переподключаем файловый handler
        _file_handler = _build_handler(SESSION_LOG)
        root_logger.addHandler(_file_handler)
        return archive_path
    except OSError as exc:
        logger.error("Failed to archive log: %s", exc)
        # Восстанавливаем handler даже если копирование упало
        _file_handler = _build_handler(SESSION_LOG)
        root_logger.addHandler(_file_handler)
        return None


def get_logger(name: str) -> logging.Logger:
    """Возвращает именованный логгер для модуля."""
    return logging.getLogger(name)