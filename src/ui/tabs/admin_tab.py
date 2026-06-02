"""
Admin tab.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.widgets.confirm_dialog import (
    ConfirmDialog,
)

from src.ui.widgets.toast import Toast

from src.ui.workers.deploy_worker import (
    DeployWorker,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AdminTab(QWidget):

    def __init__(
        self,
        controller,
    ) -> None:

        super().__init__()

        self.controller = controller

        self._build_ui()

    # ─────────────────────────────────────────────────────────────

    def _build_ui(self):

        layout = QVBoxLayout(self)

        # ─── Admin key ─────────────────────────────

        layout.addWidget(
            QLabel("Admin Private Key")
        )

        self.admin_key_input = QLineEdit()

        self.admin_key_input.setPlaceholderText(
            "0x..."
        )

        self.admin_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        layout.addWidget(
            self.admin_key_input
        )

        # ─── Deploy ────────────────────────────────

        self.deploy_button = QPushButton(
            "Compile & Deploy"
        )

        self.deploy_button.clicked.connect(
            self._deploy_contract
        )

        layout.addWidget(
            self.deploy_button
        )

        # ─── Candidate controls ───────────────────

        layout.addWidget(
            QLabel("Candidate Name")
        )

        self.candidate_name_input = (
            QLineEdit()
        )

        layout.addWidget(
            self.candidate_name_input
        )

        layout.addWidget(
            QLabel("Candidate Party")
        )

        self.candidate_party_input = (
            QLineEdit()
        )

        layout.addWidget(
            self.candidate_party_input
        )

        layout.addWidget(
            QLabel("Candidate Address")
        )

        self.candidate_address_input = (
            QLineEdit()
        )

        layout.addWidget(
            self.candidate_address_input
        )

        self.add_candidate_button = (
            QPushButton(
                "Register Candidate"
            )
        )

        self.add_candidate_button.clicked.connect(
            self._add_candidate
        )

        layout.addWidget(
            self.add_candidate_button
        )

        # ─── Voters ───────────────────────────────

        self.generate_button = QPushButton(
            "Generate Test Voters"
        )

        self.generate_button.clicked.connect(
            self._generate_voters
        )

        layout.addWidget(
            self.generate_button
        )

        self.whitelist_button = (
            QPushButton(
                "Whitelist Voters"
            )
        )

        self.whitelist_button.clicked.connect(
            self._whitelist_voters
        )

        layout.addWidget(
            self.whitelist_button
        )

        self.export_button = QPushButton(
            "Export Voters JSON"
        )

        self.export_button.clicked.connect(
            self._export_voters
        )

        layout.addWidget(
            self.export_button
        )

        self.import_button = QPushButton(
            "Import Voters JSON"
        )

        self.import_button.clicked.connect(
            self._import_voters
        )

        layout.addWidget(
            self.import_button
        )

        # ─── Stages ───────────────────────────────

        self.start_button = QPushButton(
            "Start Voting"
        )

        self.start_button.clicked.connect(
            self._start_voting
        )

        layout.addWidget(
            self.start_button
        )

        self.finish_button = QPushButton(
            "Finish Voting"
        )

        self.finish_button.clicked.connect(
            self._finish_voting
        )

        layout.addWidget(
            self.finish_button
        )

        # ─── Output ───────────────────────────────

        self.log_box = QTextEdit()

        self.log_box.setReadOnly(True)

        layout.addWidget(
            self.log_box
        )

    # ─────────────────────────────────────────────────────────────
    # Deploy
    # ─────────────────────────────────────────────────────────────

    def _deploy_contract(self):

        admin_key = (
            self.admin_key_input.text().strip()
        )

        if not admin_key:

            QMessageBox.warning(
                self,
                "Validation",
                "Admin private key required",
            )

            return

        self.deploy_button.setEnabled(False)

        self.log_box.append(
            "Starting deployment..."
        )

        self.worker = DeployWorker(
            self.controller,
            admin_key,
        )

        self.worker.progress.connect(
            self._on_progress
        )

        self.worker.finished.connect(
            self._on_deploy_success
        )

        self.worker.error.connect(
            self._on_error
        )

        self.thread = (
            self.window().thread_runner.start_worker(
                self.worker
            )
        )

    # ─────────────────────────────────────────────────────────────

    def _on_progress(self, text):

        self.log_box.append(text)

    # ─────────────────────────────────────────────────────────────

    def _on_deploy_success(
        self,
        address,
    ):

        self.deploy_button.setEnabled(True)

        self.log_box.append(
            f"Contract deployed:\n{address}"
        )

        Toast(
            self,
            "Contract deployed",
        )

    # ─────────────────────────────────────────────────────────────
    # Candidates
    # ─────────────────────────────────────────────────────────────

    def _add_candidate(self):

        try:

            key = (
                self.admin_key_input.text().strip()
            )

            name = (
                self.candidate_name_input.text().strip()
            )

            party = (
                self.candidate_party_input.text().strip()
            )

            address = (
                self.candidate_address_input.text().strip()
            )

            tx = self.controller.add_candidate(
                key,
                name,
                party,
                address,
            )

            self.log_box.append(
                f"Candidate registered:\n{tx}"
            )

            Toast(
                self,
                "Candidate added",
            )

            self.candidate_name_input.clear()
            self.candidate_party_input.clear()
            self.candidate_address_input.clear()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Candidate error",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────
    # Voters
    # ─────────────────────────────────────────────────────────────

    def _generate_voters(self):

        try:

            voters = (
                self.controller.generate_voters(
                    10
                )
            )

            self.log_box.append(
                f"Generated voters: {len(voters)}"
            )

            Toast(
                self,
                "Test voters generated",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Generation failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────

    def _whitelist_voters(self):

        key = (
            self.admin_key_input.text().strip()
        )

        try:

            tx = (
                self.controller.whitelist_voters(
                    key
                )
            )

            self.log_box.append(
                f"Whitelist TX:\n{tx}"
            )

            Toast(
                self,
                "Whitelist updated",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Whitelist failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────

    def _export_voters(self):

        dialog = ConfirmDialog(
            "Security Warning",
            (
                "Exporting voters includes "
                "private keys in plaintext JSON.\n\n"
                "Keep the file secret."
            ),
            self,
        )

        if (
            dialog.exec()
            != dialog.DialogCode.Accepted
        ):
            return

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export voters",
                "voters.json",
                "JSON (*.json)",
            )
        )

        if not path:
            return

        try:

            self.controller.export_voters(
                path
            )

            self.log_box.append(
                f"Exported voters:\n{path}"
            )

            Toast(
                self,
                "Voters exported",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Export failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────

    def _import_voters(self):

        path, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Import voters",
                "",
                "JSON (*.json)",
            )
        )

        if not path:
            return

        try:

            count = (
                self.controller.import_voters(
                    path
                )
            )

            self.log_box.append(
                f"Imported voters: {count}"
            )

            Toast(
                self,
                "Voters imported",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Import failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────
    # Stages
    # ─────────────────────────────────────────────────────────────

    def _start_voting(self):

        key = (
            self.admin_key_input.text().strip()
        )

        try:

            tx = (
                self.controller.start_voting(
                    key
                )
            )

            self.log_box.append(
                f"Voting started:\n{tx}"
            )

            Toast(
                self,
                "Voting ACTIVE",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Start failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────

    def _finish_voting(self):

        key = (
            self.admin_key_input.text().strip()
        )

        try:

            tx = (
                self.controller.finish_voting(
                    key
                )
            )

            self.log_box.append(
                f"Voting finished:\n{tx}"
            )

            Toast(
                self,
                "Voting FINISHED",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Finish failed",
                str(exc),
            )

    # ─────────────────────────────────────────────────────────────

    def _on_error(self, error):

        self.deploy_button.setEnabled(True)

        logger.error(error)

        QMessageBox.critical(
            self,
            "Operation failed",
            error,
        )