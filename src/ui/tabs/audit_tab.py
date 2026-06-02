"""
Audit tab.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.widgets.toast import Toast

from src.ui.workers.audit_worker import (
    AuditWorker,
)


class AuditTab(QWidget):

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

        self.summary_label = QLabel(
            "Audit subsystem ready"
        )

        layout.addWidget(
            self.summary_label
        )

        self.run_button = QPushButton(
            "Run Audit"
        )

        self.run_button.clicked.connect(
            self._run_audit
        )

        layout.addWidget(
            self.run_button
        )

        self.export_button = QPushButton(
            "Export Results"
        )

        self.export_button.clicked.connect(
            self._export_results
        )

        layout.addWidget(
            self.export_button
        )

        self.output = QTextEdit()

        self.output.setReadOnly(True)

        layout.addWidget(
            self.output
        )

    # ─────────────────────────────────────────────────────────────
    # Audit
    # ─────────────────────────────────────────────────────────────

    def _run_audit(self):

        self.run_button.setEnabled(False)

        self.output.clear()

        self.output.append(
            "Starting audit..."
        )

        self.worker = AuditWorker(
            self.controller
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
        report,
    ):

        self.run_button.setEnabled(True)

        self.output.clear()

        self.output.append(
            "AUDIT SUMMARY"
        )

        self.output.append(
            "=" * 40
        )

        self.output.append(
            f"Passed: {report.passed_count}"
        )

        self.output.append(
            f"Failed: {report.failed_count}"
        )

        self.output.append(
            ""
        )

        for check in report.checks:

            self.output.append(
                f"[{check.status}] "
                f"{check.check_name}"
            )

            self.output.append(
                f"Details: {check.details}"
            )

            self.output.append(
                "-" * 40
            )

        self._append_results()

        Toast(
            self,
            "Audit completed",
        )

    # ─────────────────────────────────────────────────────────────

    def _on_error(
        self,
        error,
    ):

        self.run_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Audit failed",
            error,
        )

    # ─────────────────────────────────────────────────────────────
    # Results
    # ─────────────────────────────────────────────────────────────

    def _append_results(self):

        try:

            results = (
                self.controller.get_results()
            )

            if not results:

                self.output.append(
                    "\nNo results available"
                )

                return

            self.output.append(
                "\nRESULTS"
            )

            self.output.append(
                "=" * 40
            )

            for candidate in results:

                self.output.append(
                    f"{candidate.name} | "
                    f"{candidate.party}"
                )

                self.output.append(
                    f"Votes: {candidate.vote_count}"
                )

                self.output.append(
                    f"Address: {candidate.address}"
                )

                self.output.append(
                    "-" * 40
                )

            winner = (
                self.controller.get_winner()
            )

            self.output.append(
                "\nWINNER"
            )

            self.output.append(
                "=" * 40
            )

            if winner is None:

                self.output.append(
                    "No winner"
                )

            elif winner["type"] == "tie":

                self.output.append(
                    "Tie detected"
                )

                for c in winner[
                    "candidates"
                ]:

                    self.output.append(
                        f"- {c.name}"
                    )

            else:

                c = winner["candidate"]

                self.output.append(
                    f"{c.name} "
                    f"({c.party})"
                )

        except Exception as exc:

            self.output.append(
                f"\nResult rendering failed:\n{exc}"
            )

    # ─────────────────────────────────────────────────────────────
    # Export
    # ─────────────────────────────────────────────────────────────

    def _export_results(self):

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Results",
                "results.json",
                "JSON (*.json)",
            )
        )

        if not path:
            return

        try:

            self.controller.export_results(
                path
            )

            self.output.append(
                f"\nResults exported:\n{path}"
            )

            Toast(
                self,
                "Results exported",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Export failed",
                str(exc),
            )