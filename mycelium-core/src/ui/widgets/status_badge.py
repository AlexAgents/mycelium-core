"""
StatusBadge — цветной индикатор стадии или статуса проверки.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel


# Тёмная тема: (фон, текст)
_SCHEME_DARK: dict[str, tuple[str, str]] = {
    "SETUP":         ("#2a2f3a", "#8b949e"),
    "ACTIVE":        ("#1a3a1f", "#3fb950"),
    "FINISHED":      ("#2d1b69", "#a78bfa"),
    "PASSED":        ("#1a3a1f", "#3fb950"),
    "FAILED":        ("#3d1a1a", "#f85149"),
    "WARNING":       ("#3d2f00", "#e3b341"),
    "SKIPPED":       ("#2a2f3a", "#8b949e"),
    "CONNECTED":     ("#1a3a1f", "#3fb950"),
    "DISCONNECTED":  ("#2a2f3a", "#8b949e"),
    "OFFLINE":       ("#2a2f3a", "#8b949e"),
    "DEV":           ("#1a3a1f", "#3fb950"),
    "CUSTOM":        ("#3d2f00", "#e3b341"),
}

# Светлая тема: (фон, текст)
_SCHEME_LIGHT: dict[str, tuple[str, str]] = {
    "SETUP":         ("#c4d3e8", "#1f3a68"),
    "ACTIVE":        ("#dcfce7", "#1a7f37"),
    "FINISHED":      ("#ede9fe", "#6e40c9"),
    "PASSED":        ("#dcfce7", "#1a7f37"),
    "FAILED":        ("#fee2e2", "#cf222e"),
    "WARNING":       ("#fef3e7", "#bf6a02"),
    "SKIPPED":       ("#c4d3e8", "#1f3a68"),
    "CONNECTED":     ("#dcfce7", "#1a7f37"),
    "DISCONNECTED":  ("#c4d3e8", "#1f3a68"),
    "OFFLINE":       ("#c4d3e8", "#1f3a68"),
    "DEV":           ("#dcfce7", "#1a7f37"),
    "CUSTOM":        ("#fef3e7", "#bf6a02"),
}


def _detect_light_theme() -> bool:
    """
    Определяет текущую тему через property у QApplication.
    MainWindow при apply_theme устанавливает app._theme_mode.
    """
    app = QApplication.instance()
    if app is None:
        return False
    return getattr(app, "_theme_mode", "dark") == "light"


class StatusBadge(QLabel):
    """
    Цветная пилюля-индикатор.
    Автоматически подбирает палитру под текущую тему.
    """

    def __init__(self, text: str) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(text)

    def setText(self, text: str) -> None:  # type: ignore[override]
        super().setText(f" {text.upper()} ")
        self._apply_style(text.upper())

    def _apply_style(self, key: str) -> None:
        scheme = (
            _SCHEME_LIGHT if _detect_light_theme() else _SCHEME_DARK
        )
        bg, fg = scheme.get(key, scheme["SETUP"])

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                border: none;
            }}
            """
        )

    def refresh_theme(self) -> None:
        """Перерисовать с учётом текущей темы (вызвать при смене темы)."""
        # Восстанавливаем последнюю надпись без " " по краям
        current = self.text().strip()
        self._apply_style(current)