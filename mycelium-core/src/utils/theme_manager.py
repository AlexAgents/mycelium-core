"""
Менеджер тем.
"""

from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.utils.paths import THEMES_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ThemeManager:
    def __init__(
        self,
        app: QApplication,
    ) -> None:
        self.app = app
        self.current_theme = "dark"

    def apply_theme(
        self,
        theme_name: str,
    ) -> None:

        path = THEMES_DIR / f"{theme_name}.qss"
        if not path.exists():

            raise FileNotFoundError(
                f"Theme not found: {path}"
            )

        self.app.setStyleSheet(
            path.read_text(
                encoding="utf-8"
            )
        )
        self.current_theme = theme_name
        logger.info(
            "Theme applied: %s",
            theme_name,
        )