"""
Главное окно MYCELIUM CORE.
"""

from __future__ import annotations

import traceback

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.app_controller import AppController

from src.ui.tabs.admin_tab import AdminTab
from src.ui.tabs.audit_tab import AuditTab
from src.ui.tabs.vote_tab import VoteTab

from src.ui.widgets.status_badge import (
    StatusBadge,
)

from src.ui.workers.thread_runner import (
    ThreadRunner,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):

    def __init__(
        self,
        controller: AppController,
    ) -> None:

        super().__init__()

        self.controller = controller

        self.thread_runner = ThreadRunner()

        self.setWindowTitle(
            "MYCELIUM CORE"
        )

        self.setMinimumSize(1100, 700)

        self._build_ui()

        self._start_status_timer()

    # ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:

        root = QWidget()

        layout = QVBoxLayout(root)

        topbar = QHBoxLayout()

        self.theme_button = QPushButton(
            "Toggle Theme"
        )

        self.theme_button.clicked.connect(
            self._toggle_theme
        )

        topbar.addWidget(
            self.theme_button
        )

        topbar.addStretch()

        layout.addLayout(topbar)

        self.tabs = QTabWidget()

        self.admin_tab = AdminTab(
            self.controller
        )

        self.vote_tab = VoteTab(
            self.controller
        )

        self.audit_tab = AuditTab(
            self.controller
        )

        self.tabs.addTab(
            self.admin_tab,
            "Admin",
        )

        self.tabs.addTab(
            self.vote_tab,
            "Vote",
        )

        self.tabs.addTab(
            self.audit_tab,
            "Audit",
        )

        layout.addWidget(
            self.tabs
        )

        self.setCentralWidget(root)

        self._build_statusbar()

    # ─────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:

        status = QStatusBar()

        self.rpc_label = QLabel(
            "RPC: disconnected"
        )

        self.block_label = QLabel(
            "Block: -"
        )

        self.client_label = QLabel(
            "Client: unknown"
        )

        self.contract_label = QLabel(
            "Contract: not deployed"
        )

        self.stage_badge = StatusBadge(
            "SETUP"
        )

        status.addPermanentWidget(
            self.rpc_label
        )

        status.addPermanentWidget(
            self.block_label
        )

        status.addPermanentWidget(
            self.client_label
        )

        status.addPermanentWidget(
            self.stage_badge
        )

        status.addPermanentWidget(
            self.contract_label,
            1,
        )

        self.setStatusBar(status)

    # ─────────────────────────────────────────────────────────────

    def _start_status_timer(self) -> None:

        self.timer = QTimer()

        self.timer.timeout.connect(
            self._refresh_status
        )

        self.timer.start(2000)

    # ─────────────────────────────────────────────────────────────

    def _refresh_status(self) -> None:

        try:

            connected = (
                self.controller.get_rpc_status()
            )

            self.rpc_label.setText(
                f"RPC: {'connected' if connected else 'offline'}"
            )

            block = (
                self.controller.get_block_number()
            )

            self.block_label.setText(
                f"Block: {block}"
            )

            contract = (
                self.controller.session.contract_address
            )

            if contract:

                self.contract_label.setText(
                    f"Contract: {contract}"
                )

            try:

                stage = (
                    self.controller.get_stage()
                )

                self.stage_badge.setText(
                    stage.name
                )

            except Exception:
                pass

            try:

                client = (
                    self.controller.provider.client_version()
                )

                self.client_label.setText(
                    f"Client: {client}"
                )

            except Exception:
                pass

        except Exception:

            logger.error(
                "Status refresh failed:\n%s",
                traceback.format_exc(),
            )

    # ─────────────────────────────────────────────────────────────

    def _toggle_theme(self):

        app = self.window().app

        current = getattr(
            app,
            "_theme_mode",
            "dark",
        )

        next_theme = (
            "light"
            if current == "dark"
            else "dark"
        )

        app.theme_manager.apply_theme(
            next_theme
        )

        app._theme_mode = next_theme

    # ─────────────────────────────────────────────────────────────

    def closeEvent(self, event):

        try:

            self.controller.shutdown()

        finally:

            super().closeEvent(event)