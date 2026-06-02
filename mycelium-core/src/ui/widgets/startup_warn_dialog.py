"""
StartupWarnDialog — предупреждение о большом объёме chain-data при старте.
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


class StartupWarnDialog(QDialog):
    """Предупреждение о большом chain-data при запуске."""

    def __init__(self, parent, size_mb: float) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("startup.warn.title"))
        self.setMinimumWidth(460)
        self.setModal(True)

        self._dont_show_again = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 16)
        layout.setSpacing(14)

        # ── Header: icon + text ───────────────────────────────
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

        msg_lbl = QLabel(
            t("startup.warn.msg", size=f"{size_mb:.1f}")
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("messageDialogText")
        msg_lbl.setMinimumWidth(340)
        header_row.addWidget(msg_lbl, 1)

        layout.addLayout(header_row)

        # ── "Don't show again" ─────────────────────────────────
        self._dont_show_cb = QCheckBox(t("startup.warn.dont_show"))
        self._dont_show_cb.setChecked(False)
        layout.addWidget(self._dont_show_cb)

        # ── Close button (центр) ───────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        close_btn = QPushButton(" " + t("common.ok"))
        close_btn.setMinimumWidth(120)
        if _QTA:
            close_btn.setIcon(
                qta.icon("fa5s.check", color="#58a6ff")
            )
            close_btn.setIconSize(QSize(14, 14))
        close_btn.clicked.connect(self._on_close)
        btn_row.addWidget(close_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_close(self) -> None:
        self._dont_show_again = self._dont_show_cb.isChecked()
        self.accept()

    @property
    def dont_show_again(self) -> bool:
        return self._dont_show_again