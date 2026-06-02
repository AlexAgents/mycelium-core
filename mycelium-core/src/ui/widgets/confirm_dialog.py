"""
ConfirmDialog — диалог подтверждения с переводимыми кнопками.
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


class ConfirmDialog(QDialog):
    """
    Диалог подтверждения.

    Кнопки переводимы через i18n (common.confirm / common.cancel).
    Confirm — слева, акцентирован стилем deployButton.
    Cancel — справа, нейтральная.
    """

    def __init__(
        self,
        title: str,
        message: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 16)
        layout.setSpacing(14)

        # ── Icon + text ────────────────────────────────────────
        body_row = QHBoxLayout()
        body_row.setSpacing(14)

        if _QTA:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon(
                    "fa5s.exclamation-triangle",
                    color="#bf8700",
                ).pixmap(QSize(40, 40))
            )
            icon_lbl.setFixedSize(44, 44)
            body_row.addWidget(icon_lbl)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setObjectName("messageDialogText")
        label.setMinimumWidth(320)
        body_row.addWidget(label, 1)

        layout.addLayout(body_row)

        # ── Buttons (Confirm | Cancel, по центру) ──────────────
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()

        self.confirm_button = QPushButton(
            " " + t("common.confirm")
        )
        self.confirm_button.setObjectName("deployButton")
        self.confirm_button.setMinimumWidth(130)
        self.confirm_button.setFixedHeight(32)
        if _QTA:
            self.confirm_button.setIcon(
                qta.icon("fa5s.check", color="#ffffff")
            )
            self.confirm_button.setIconSize(QSize(14, 14))
        self.confirm_button.clicked.connect(self.accept)
        buttons.addWidget(self.confirm_button)

        self.cancel_button = QPushButton(
            " " + t("common.cancel")
        )
        self.cancel_button.setMinimumWidth(130)
        self.cancel_button.setFixedHeight(32)
        if _QTA:
            self.cancel_button.setIcon(
                qta.icon("fa5s.times", color="#8b949e")
            )
            self.cancel_button.setIconSize(QSize(14, 14))
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_button)

        buttons.addStretch()
        layout.addLayout(buttons)