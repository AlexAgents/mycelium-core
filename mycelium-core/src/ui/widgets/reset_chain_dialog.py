"""
ResetChainDialog — подтверждение сброса blockchain-данных.

Показывает статистику (контракты, сессии, размер).
Позволяет опционально удалить архивные логи.
"""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
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


class ResetChainDialog(QDialog):
    """Подтверждение сброса blockchain-данных."""

    def __init__(self, parent, stats: dict) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("reset.dialog.title"))
        self.setMinimumWidth(480)
        self.setModal(True)

        self._confirmed = False
        self._delete_logs = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 16)
        layout.setSpacing(14)

        # ── Header: icon + title ───────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        if _QTA:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon(
                    "fa5s.exclamation-triangle", color="#bf8700"
                ).pixmap(QSize(40, 40))
            )
            icon_lbl.setFixedSize(44, 44)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            header_row.addWidget(icon_lbl)

        msg_lbl = QLabel(t("reset.dialog.msg"))
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("messageDialogText")
        msg_lbl.setMinimumWidth(360)
        header_row.addWidget(msg_lbl, 1)

        layout.addLayout(header_row)

        # ── Optional: delete logs ──────────────────────────────
        self._delete_logs_cb = QCheckBox(t("reset.dialog.delete_logs"))
        self._delete_logs_cb.setChecked(False)
        layout.addWidget(self._delete_logs_cb)

        # ── Buttons (по центру) ────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        # Сначала Очистить потом Отмена
        confirm_btn = QPushButton(" " + t("reset.dialog.confirm"))
        confirm_btn.setObjectName("deployButton")
        confirm_btn.setMinimumWidth(130)
        confirm_btn.setFixedHeight(32)
        if _QTA:
            confirm_btn.setIcon(
                qta.icon("fa5s.trash", color="#ffffff")
            )
            confirm_btn.setIconSize(QSize(14, 14))
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn)

        cancel_btn = QPushButton(" " + t("common.cancel"))
        cancel_btn.setMinimumWidth(130)
        cancel_btn.setFixedHeight(32)
        if _QTA:
            cancel_btn.setIcon(
                qta.icon("fa5s.times", color="#8b949e")
            )
            cancel_btn.setIconSize(QSize(14, 14))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_confirm(self) -> None:
        self._confirmed = True
        self._delete_logs = self._delete_logs_cb.isChecked()
        self.accept()

    @property
    def confirmed(self) -> bool:
        return self._confirmed

    @property
    def delete_logs(self) -> bool:
        return self._delete_logs