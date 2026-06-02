"""
RegisterCandidatesWorker — фоновая регистрация кандидатов on-chain.
"""
from __future__ import annotations

from src.ui.workers.base_worker import BaseWorker


class RegisterCandidatesWorker(BaseWorker):
    """
    Принимает список (name, party, address) и последовательно
    вызывает controller.add_candidate для каждого.
    Ключ администратора очищается после завершения.
    """

    def __init__(
        self,
        controller,
        admin_key: str,
        candidates: list[tuple[str, str, str]],
    ) -> None:
        super().__init__()
        self.controller = controller
        self._admin_key = admin_key
        self.candidates = candidates

    def run(self) -> None:
        try:
            total = len(self.candidates)
            for idx, (name, party, address) in enumerate(
                self.candidates, 1
            ):
                self.progress.emit(
                    f"Registering {name} ({idx}/{total})..."
                )
                self.controller.add_candidate(
                    self._admin_key, name, party, address
                )
                pct = int(idx / total * 100)
                self.percent.emit(pct)

            self.finished.emit(total)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self._admin_key = ""