"""
MassVoteWorker -- фоновое массовое голосование.

Last Hotfix:
  - Предварительная фильтрация (whitelist + balance)
  - Продолжение при ошибках отдельных избирателей
  - Итоговая статистика: voted / skipped_whitelist /
    skipped_balance / failed
"""
from __future__ import annotations

import random
from typing import Optional

from src.ui.workers.base_worker import BaseWorker
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Минимальный баланс для оплаты газа castVote (300k gas * 1 gwei)
_MIN_BALANCE_WEI = 300_000 * 1_000_000_000  # 0.0003 ETH


class MassVoteWorker(BaseWorker):
    """
    Массовое голосование с предварительной фильтрацией.

    Каждый избиратель проверяется:
      1. Есть ли private_key
      2. Есть ли в whitelist
      3. Достаточен ли баланс для газа
      4. Не голосовал ли ранее

    При ошибке конкретного избирателя цикл продолжается.

    Сигналы:
        progress(str)  -- текстовый лог
        percent(int)   -- процент 0..100
        finished(dict) -- итоговая статистика
        error(str)     -- критическая ошибка (прерывание)
    """

    def __init__(
        self,
        controller,
        voters: list[dict],
        candidate_addresses: list[str],
        seed: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.controller = controller
        self._voters = list(voters)
        self._candidate_addresses = list(candidate_addresses)
        self._seed = seed

    def run(self) -> None:
        try:
            if not self._voters:
                self.error.emit("No voters provided.")
                return

            if not self._candidate_addresses:
                self.error.emit("No candidates registered.")
                return

            rng = random.Random(self._seed)
            total = len(self._voters)

            voted = 0
            skipped_no_key = 0
            skipped_whitelist = 0
            skipped_balance = 0
            skipped_already_voted = 0
            failed = 0
            errors: list[str] = []

            self.progress.emit(
                f"Mass vote: {total} voter(s), "
                f"{len(self._candidate_addresses)} candidate(s)"
            )
            self.progress.emit(
                "Pre-filtering voters (whitelist + balance)..."
            )

            for idx, voter in enumerate(self._voters, 1):
                address = voter.get("address", "?")
                private_key = voter.get("private_key")
                short = f"{address[:8]}...{address[-4:]}"

                # --- Filter 1: private key ---
                if not private_key:
                    skipped_no_key += 1
                    self._emit_pct(idx, total)
                    continue

                # --- Filter 2: whitelist ---
                try:
                    if not self.controller.is_whitelisted(address):
                        skipped_whitelist += 1
                        self._emit_pct(idx, total)
                        continue
                except Exception:
                    skipped_whitelist += 1
                    self._emit_pct(idx, total)
                    continue

                # --- Filter 3: already voted ---
                try:
                    if self.controller.has_voted(address):
                        skipped_already_voted += 1
                        self._emit_pct(idx, total)
                        continue
                except Exception:
                    pass

                # --- Filter 4: balance ---
                try:
                    balance = self.controller.get_balance_wei(
                        address
                    )
                    if balance < _MIN_BALANCE_WEI:
                        skipped_balance += 1
                        self._emit_pct(idx, total)
                        continue
                except Exception:
                    skipped_balance += 1
                    self._emit_pct(idx, total)
                    continue

                # --- Cast vote ---
                candidate = rng.choice(
                    self._candidate_addresses
                )
                short_c = f"{candidate[:8]}...{candidate[-4:]}"

                try:
                    self.progress.emit(
                        f"[{idx}/{total}] "
                        f"{short} -> {short_c}"
                    )
                    self.controller.cast_vote(
                        private_key, candidate
                    )
                    voted += 1
                except Exception as exc:
                    msg = f"{short}: {exc}"
                    errors.append(msg)
                    failed += 1
                    self.progress.emit(
                        f"  [!] Failed: {msg[:80]}"
                    )

                self._emit_pct(idx, total)

            # --- Summary ---
            total_skipped = (
                skipped_no_key
                + skipped_whitelist
                + skipped_balance
                + skipped_already_voted
            )

            lines = [
                "",
                "--- Mass Vote Results ---",
                f"  Voted successfully: {voted}",
            ]
            if skipped_whitelist > 0:
                lines.append(
                    f"  Skipped (not whitelisted): "
                    f"{skipped_whitelist}"
                )
            if skipped_balance > 0:
                lines.append(
                    f"  Skipped (insufficient balance): "
                    f"{skipped_balance}"
                )
            if skipped_already_voted > 0:
                lines.append(
                    f"  Skipped (already voted): "
                    f"{skipped_already_voted}"
                )
            if skipped_no_key > 0:
                lines.append(
                    f"  Skipped (no private key): "
                    f"{skipped_no_key}"
                )
            if failed > 0:
                lines.append(
                    f"  Failed (TX error): {failed}"
                )
            lines.append(
                f"  Total processed: {total}"
            )

            for line in lines:
                self.progress.emit(line)

            self.finished.emit({
                "voted": voted,
                "skipped_whitelist": skipped_whitelist,
                "skipped_balance": skipped_balance,
                "skipped_already_voted": skipped_already_voted,
                "skipped_no_key": skipped_no_key,
                "failed": failed,
                "total": total,
                "errors": errors,
            })

        except Exception as exc:
            self.error.emit(str(exc))

    def _emit_pct(self, current: int, total: int) -> None:
        if total > 0:
            self.percent.emit(int(current / total * 100))