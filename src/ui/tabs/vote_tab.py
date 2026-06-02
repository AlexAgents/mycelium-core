"""
Vote tab.
"""

from __future__ import annotations

from eth_account import Account

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

from src.ui.widgets.toast import Toast

from src.ui.workers.vote_worker import (
    VoteWorker,
)

from src.utils.validators import (
    is_valid_eth_address,
    is_valid_private_key,
)


class VoteTab(QWidget):

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

        layout.addWidget(
            QLabel("Voter Private Key")
        )

        self.private_key_input = QLineEdit()

        self.private_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.private_key_input.textChanged.connect(
            self._refresh_voter_status
        )

        layout.addWidget(
            self.private_key_input
        )

        self.status_box = QTextEdit()

        self.status_box.setReadOnly(True)

        layout.addWidget(
            self.status_box
        )

        self.refresh_candidates_button = (
            QPushButton(
                "Load Candidates"
            )
        )

        self.refresh_candidates_button.clicked.connect(
            self._load_candidates
        )

        layout.addWidget(
            self.refresh_candidates_button
        )

        layout.addWidget(
            QLabel("Candidate Address")
        )

        self.candidate_input = QLineEdit()

        layout.addWidget(
            self.candidate_input
        )

        self.vote_button = QPushButton(
            "CAST VOTE"
        )

        self.vote_button.clicked.connect(
            self._cast_vote
        )

        layout.addWidget(
            self.vote_button
        )

        self.save_qr_button = QPushButton(
            "Save QR"
        )

        self.save_qr_button.setEnabled(False)

        self.save_qr_button.clicked.connect(
            self._save_qr
        )

        layout.addWidget(
            self.save_qr_button
        )

        self.output = QTextEdit()

        self.output.setReadOnly(True)

        layout.addWidget(
            self.output
        )

    # ─────────────────────────────────────────────────────────────
    # Voting
    # ─────────────────────────────────────────────────────────────

    def _cast_vote(self):

        private_key = (
            self.private_key_input.text().strip()
        )

        candidate = (
            self.candidate_input.text().strip()
        )

        if not is_valid_private_key(
            private_key
        ):

            QMessageBox.warning(
                self,
                "Validation",
                "Invalid private key",
            )

            return

        if not is_valid_eth_address(
            candidate
        ):

            QMessageBox.warning(
                self,
                "Validation",
                "Invalid candidate address",
            )

            return

        self.vote_button.setEnabled(False)

        self.worker = VoteWorker(
            self.controller,
            private_key,
            candidate,
        )

        self.worker.progress.connect(
            self.output.append
        )

        self.worker.finished.connect(
            self._on_success
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

    def _on_success(
        self,
        receipt,
    ):

        self.vote_button.setEnabled(True)

        self.private_key_input.clear()

        self.output.append(
            f"Vote successful\nTX:\n{receipt.tx_hash}"
        )

        self.last_receipt = receipt

        if receipt.qr_bytes:

            self.save_qr_button.setEnabled(
                True
            )

        Toast(
            self,
            "Vote submitted",
        )

    # ─────────────────────────────────────────────────────────────

    def _on_error(self, error):

        self.vote_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Vote failed",
            error,
        )

    # ─────────────────────────────────────────────────────────────
    # Candidate list
    # ─────────────────────────────────────────────────────────────

    def _load_candidates(self):

        self.output.clear()

        try:

            candidates = (
                self.controller.get_candidates()
            )

            if not candidates:

                self.output.append(
                    "No candidates registered"
                )

                return

            for c in candidates:

                self.output.append(
                    f"{c.name} | "
                    f"{c.party} | "
                    f"{c.address}"
                )

        except Exception as exc:

            self.output.append(
                f"ERROR:\n{exc}"
            )

    # ─────────────────────────────────────────────────────────────
    # QR
    # ─────────────────────────────────────────────────────────────

    def _save_qr(self):

        if not hasattr(
            self,
            "last_receipt",
        ):
            return

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Save QR",
                "receipt.png",
                "PNG (*.png)",
            )
        )

        if not path:
            return

        with open(path, "wb") as f:

            f.write(
                self.last_receipt.qr_bytes
            )

        QMessageBox.information(
            self,
            "Saved",
            f"QR saved:\n{path}",
        )

    # ─────────────────────────────────────────────────────────────
    # Voter status
    # ─────────────────────────────────────────────────────────────

    def _refresh_voter_status(self):

        self.status_box.clear()

        key = (
            self.private_key_input.text().strip()
        )

        if not key:
            return

        try:

            account = Account.from_key(key)

            addr = account.address

            whitelisted = (
                self.controller.is_whitelisted(
                    addr
                )
            )

            voted = (
                self.controller.has_voted(
                    addr
                )
            )

            self.status_box.append(
                f"Address:\n{addr}"
            )

            self.status_box.append(
                f"\nWhitelisted: {whitelisted}"
            )

            self.status_box.append(
                f"Has voted: {voted}"
            )

        except Exception:

            self.status_box.append(
                "Invalid private key"
            )