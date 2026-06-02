"""
Runtime i18n manager.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.utils.paths import I18N_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


class I18N:

    def __init__(
        self,
        language: str = "ru",
    ) -> None:

        self.language = language

        self._translations = {}

        self.load(language)

    # ─────────────────────────────────────────────────────────────

    def load(
        self,
        language: str,
    ) -> None:

        path = I18N_DIR / f"{language}.json"

        if not path.exists():

            raise FileNotFoundError(
                f"Translation file not found: {path}"
            )

        self._translations = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        self.language = language

        logger.info(
            "Language loaded: %s",
            language,
        )

    # ─────────────────────────────────────────────────────────────

    def t(
        self,
        key: str,
    ) -> str:

        return self._translations.get(
            key,
            key,
        )