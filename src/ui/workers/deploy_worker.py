"""
Deploy.
"""
from src.ui.workers.base_worker import BaseWorker


class DeployWorker(BaseWorker):
    def __init__(
        self,
        controller,
        admin_key: str,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._admin_key = admin_key

    def run(self) -> None:
        try:
            self.progress.emit("Compiling contract...")
            self.controller.compile_contract()
            self.progress.emit("Deploying contract...")
            address = self.controller.deploy_contract(self._admin_key)
            self.finished.emit(address)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            # FIX: ключ живёт в объекте воркера только до конца run()
            self._admin_key = ""