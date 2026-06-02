"""
MessageDialog — унифицированный диалог сообщений.

Заменяет стандартный QMessageBox.
Иконки qtawesome, переводимые кнопки, выравнивание по центру.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QSize, Qt
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


# kind -> (icon_name, color)
_ICONS: dict[str, tuple[str, str]] = {
    "info":     ("fa5s.info-circle",         "#0969da"),
    "warning":  ("fa5s.exclamation-triangle", "#bf8700"),
    "error":    ("fa5s.times-circle",        "#cf222e"),
    "success":  ("fa5s.check-circle",        "#2da44e"),
    "question": ("fa5s.question-circle",     "#0969da"),
}


class MessageDialog(QDialog):
    """
    Унифицированный диалог сообщений.

    Использование:
        dlg = MessageDialog(
            parent,
            kind="question",
            title="Подтверждение",
            text="Продолжить?",
            buttons=[("common.yes", "yes"), ("common.no", "no")],
            default_button_id="no",
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_id == "yes":
            ...
    """

    def __init__(
        self,
        parent,
        *,
        kind: str = "info",
        title: str = "",
        text: str = "",
        buttons: list[tuple[str, str]] | None = None,
        default_button_id: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self.setModal(True)

        self.result_id: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 14)
        layout.setSpacing(14)

        # ── Icon + text ────────────────────────────────────────
        body_row = QHBoxLayout()
        body_row.setSpacing(14)

        if _QTA and kind in _ICONS:
            icon_name, color = _ICONS[kind]
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon(icon_name, color=color).pixmap(
                    QSize(40, 40)
                )
            )
            icon_lbl.setFixedSize(44, 44)
            icon_lbl.setAlignment(
                Qt.AlignmentFlag.AlignTop
                | Qt.AlignmentFlag.AlignHCenter
            )
            body_row.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setObjectName("messageDialogText")
        text_lbl.setMinimumWidth(320)
        body_row.addWidget(text_lbl, 1)

        layout.addLayout(body_row)

        # ── Buttons (центрированы) ─────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if buttons is None:
            buttons = [("common.ok", "ok")]

        self._buttons: dict[str, QPushButton] = {}
        for i18n_key, btn_id in buttons:
            btn = QPushButton(t(i18n_key))
            btn.setMinimumWidth(110)
            btn.setFixedHeight(32)
            if btn_id == default_button_id:
                btn.setObjectName("deployButton")
                btn.setDefault(True)
            btn.clicked.connect(
                lambda _, bid=btn_id: self._on_button(bid)
            )
            btn_row.addWidget(btn)
            self._buttons[btn_id] = btn
            
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_button(self, button_id: str) -> None:
        self.result_id = button_id
        self.accept()