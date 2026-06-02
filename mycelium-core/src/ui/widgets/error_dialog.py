"""
ErrorDialog — диалог ошибки с предложением действия.
"""
from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.utils.i18n import t


class ErrorDialog(QDialog):
    """
    Диалог ошибки с опциональной кнопкой действия.

    Attributes:
        action_accepted: True если пользователь нажал кнопку действия.
    """

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        action_text: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self.action_accepted = False

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Icon + message
        msg_row = QHBoxLayout()
        if _QTA:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon(
                    "fa5s.exclamation-circle", color="#f85149"
                ).pixmap(QSize(32, 32))
            )
            msg_row.addWidget(icon_lbl)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 13px;")
        msg_row.addWidget(msg_label, 1)
        layout.addLayout(msg_row)

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()

        if action_text:
            action_btn = QPushButton(action_text)
            action_btn.setObjectName("deployButton")
            if _QTA:
                action_btn.setIcon(
                    qta.icon("fa5s.wrench", color="#ffffff")
                )
                action_btn.setIconSize(QSize(14, 14))
            action_btn.clicked.connect(self._on_action)
            buttons.addWidget(action_btn)

        close_btn = QPushButton(t("common.close"))
        close_btn.clicked.connect(self.reject)
        buttons.addWidget(close_btn)

        layout.addLayout(buttons)

    def _on_action(self) -> None:
        self.action_accepted = True
        self.accept()