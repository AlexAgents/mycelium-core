"""
AboutDialog — окно с информацией о проекте.
"""
from __future__ import annotations

import webbrowser

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
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
from src.utils.paths import BUNDLE_DIR


APP_VERSION = "1.0.1"

AUTHOR_NAME = "AlexAgents"
GITHUB_URL = "https://github.com/AlexAgents/mycelium-core"


class AboutDialog(QDialog):
    """Краткая информация о приложении."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("about.title"))
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 18)
        layout.setSpacing(16)

        # ── Header row: logo + title block ────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(18)

        # Logo
        logo_path = BUNDLE_DIR / "src" / "assets" / "icons" / "Original.png"
        if logo_path.exists():
            logo_lbl = QLabel()
            pixmap = QPixmap(str(logo_path)).scaled(
                96, 96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_lbl.setPixmap(pixmap)
            logo_lbl.setFixedSize(96, 96)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_row.addWidget(logo_lbl)
        elif _QTA:
            # Fallback — иконка qtawesome
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon("fa5s.cube", color="#388bfd").pixmap(
                    QSize(64, 64)
                )
            )
            header_row.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title_lbl = QLabel("MYCELIUM CORE")
        title_lbl.setObjectName("aboutTitle")
        title_lbl.setStyleSheet(
            "font-size: 18px; font-weight: bold; "
            "letter-spacing: 2px;"
        )
        title_col.addWidget(title_lbl)

        version_lbl = QLabel(
            f"{t('about.version_label')}: {APP_VERSION}"
        )
        version_lbl.setObjectName("aboutVersion")
        version_lbl.setStyleSheet("font-size: 11px;")
        title_col.addWidget(version_lbl)

        author_lbl = QLabel(
            f"{t('about.author')}: {AUTHOR_NAME}"
        )
        author_lbl.setObjectName("aboutVersion")
        author_lbl.setStyleSheet("font-size: 11px;")
        title_col.addWidget(author_lbl)

        title_col.addStretch()

        header_row.addLayout(title_col)
        header_row.addStretch()
        layout.addLayout(header_row)

        # ── Body ───────────────────────────────────────────────
        body_lbl = QLabel(t("about.body"))
        body_lbl.setWordWrap(True)
        body_lbl.setObjectName("aboutBody")
        layout.addWidget(body_lbl)

        # ── Buttons (по центру): GitHub + Close ───────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        github_btn = QPushButton(" GitHub")
        github_btn.setObjectName("iconButton")
        if _QTA:
            github_btn.setIcon(
                qta.icon("fa5b.github", color="#58a6ff")
            )
            github_btn.setIconSize(QSize(16, 16))
        github_btn.setMinimumWidth(120)
        github_btn.setToolTip(t("about.github"))
        github_btn.clicked.connect(self._open_github)
        btn_row.addWidget(github_btn)

        close_btn = QPushButton(" " + t("common.close"))
        close_btn.setObjectName("iconButton")
        if _QTA:
            close_btn.setIcon(
                qta.icon("fa5s.check", color="#58a6ff")
            )
            close_btn.setIconSize(QSize(15, 15))
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _open_github(self) -> None:
        try:
            webbrowser.open(GITHUB_URL)
        except Exception:
            pass