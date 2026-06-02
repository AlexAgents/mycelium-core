"""
Vote worker.
"""
from src.ui.workers.base_worker import BaseWorker


class VoteWorker(BaseWorker):
    def __init__(
        self,
        controller,
        private_key: str,
        candidate_address: str,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._private_key = private_key
        self.candidate_address = candidate_address

    def run(self) -> None:
        try:
            self.progress.emit("Submitting vote...")
            receipt = self.controller.cast_vote(
                self._private_key,
                self.candidate_address,
            )
            self.finished.emit(receipt)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            # FIX: ключ живёт в объекте воркера только до конца run()
            self._private_key = ""