"""
Audit worker.
"""

from src.ui.workers.base_worker import BaseWorker


class AuditWorker(BaseWorker):

    def __init__(
        self,
        controller,
    ) -> None:

        super().__init__()

        self.controller = controller

    def run(self):

        try:

            self.progress.emit(
                "Running security audit..."
            )

            report = self.controller.run_audit()

            self.finished.emit(report)

        except Exception as exc:

            self.error.emit(str(exc))