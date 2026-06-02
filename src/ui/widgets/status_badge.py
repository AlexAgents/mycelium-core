"""
Status badge widget.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class StatusBadge(QLabel):

    COLORS = {
        "PASSED": "#2ecc71",
        "FAILED": "#e74c3c",
        "WARNING": "#f39c12",
        "ACTIVE": "#3498db",
        "SETUP": "#7f8c8d",
        "FINISHED": "#9b59b6",
    }

    def __init__(
        self,
        text: str,
    ) -> None:

        super().__init__(text)

        self._apply_style(text)

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

    # ─────────────────────────────────────────────────────────────

    def setText(
        self,
        text: str,
    ) -> None:

        super().setText(text)

        self._apply_style(text)

    # ─────────────────────────────────────────────────────────────

    def _apply_style(
        self,
        text: str,
    ) -> None:

        color = self.COLORS.get(
            text.upper(),
            "#777",
        )

        self.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: white;
                padding: 4px 12px;
                border-radius: 10px;
                font-weight: bold;
            }}
        """)