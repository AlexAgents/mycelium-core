"""
Runtime i18n manager.

Эмитит сигнал languageChanged при смене языка.
Все переводимые виджеты подписываются на этот сигнал
и вызывают свой retranslate_ui() для обновления текста.

API:
    init_i18n(language)  - вызывается один раз при старте
    get_i18n()           - возвращает синглтон
    t(key, **kwargs)     - shortcut: get_i18n().t(key, ...)
"""
from __future__ import annotations

import json
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.utils.paths import I18N_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


class I18N(QObject):
    """Менеджер переводов с поддержкой смены языка на "лету"."""

    languageChanged = pyqtSignal(str)

    def __init__(self, language: str = "ru") -> None:
        super().__init__()
        self.language = language
        self._translations: dict[str, str] = {}
        self._load_from_file(language)

    # ─────────────────────────────────────────────────────────────
    def _load_from_file(self, language: str) -> None:
        path = I18N_DIR / f"{language}.json"
        if not path.exists():
            raise FileNotFoundError(
                f"Translation file not found: {path}"
            )
        self._translations = json.loads(
            path.read_text(encoding="utf-8")
        )
        self.language = language
        logger.info("Language loaded: %s", language)

    def load(self, language: str) -> None:
        """
        Загружает новый язык и эмитит сигнал.
        Безопасно для повторного вызова с тем же языком.
        """
        if language == self.language and self._translations:
            return
        self._load_from_file(language)
        self.languageChanged.emit(language)

    def t(self, key: str, **kwargs) -> str:
        """
        Возвращает перевод по ключу.
        Поддерживает подстановку: t("key", count=5)
        Если ключ не найден — возвращает сам ключ.
        """
        text = self._translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                pass
        return text


# ─────────────────────────────────────────────────────────────────
# Singleton accessors
# ─────────────────────────────────────────────────────────────────

_i18n_instance: Optional[I18N] = None


def init_i18n(language: str) -> I18N:
    """Инициализация синглтона. Вызывается из main()."""
    global _i18n_instance
    _i18n_instance = I18N(language)
    return _i18n_instance


def get_i18n() -> I18N:
    """Возвращает текущий инстанс. Бросает если не инициализирован."""
    if _i18n_instance is None:
        raise RuntimeError("I18N not initialized — call init_i18n() first")
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """Shortcut: get_i18n().t(key, **kwargs)."""
    return get_i18n().t(key, **kwargs)