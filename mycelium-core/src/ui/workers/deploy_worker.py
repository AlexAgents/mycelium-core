"""
Worker деплоя контракта.
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
            self.percent.emit(20)
            self.controller.compile_contract()

            self.progress.emit("Deploying contract...")
            self.percent.emit(60)
            address = self.controller.deploy_contract(self._admin_key)

            self.percent.emit(100)
            self.finished.emit(address)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self._admin_key = ""