"""
Toast widget.
"""

from PyQt6.QtCore import (
    QPropertyAnimation,
    QTimer,
)
from PyQt6.QtWidgets import QLabel


class Toast(QLabel):

    def __init__(
        self,
        parent,
        text: str,
    ) -> None:

        super().__init__(text, parent)

        self.setStyleSheet("""
            QLabel {
                background: #222;
                color: white;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 13px;
            }
        """)

        self.adjustSize()

        self.move(20, 20)

        self.show()

        self.fade_in()

        QTimer.singleShot(
            3000,
            self.fade_out,
        )

    # ─────────────────────────────────────────────────────────────

    def fade_in(self):

        self.anim = QPropertyAnimation(
            self,
            b"windowOpacity",
        )

        self.anim.setDuration(250)

        self.anim.setStartValue(0.0)

        self.anim.setEndValue(1.0)

        self.anim.start()

    # ─────────────────────────────────────────────────────────────

    def fade_out(self):

        self.anim = QPropertyAnimation(
            self,
            b"windowOpacity",
        )

        self.anim.setDuration(500)

        self.anim.setStartValue(1.0)

        self.anim.setEndValue(0.0)

        self.anim.finished.connect(
            self.close
        )

        self.anim.start()