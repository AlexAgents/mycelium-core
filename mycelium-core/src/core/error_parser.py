"""
ErrorParser — структурированный парсинг RPC/контрактных ошибок Ethereum.

Бизнес-логика. Используется AppController.
Возвращает i18n-ключи (без обращения к самой системе i18n) —
UI делает t(key) самостоятельно.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParsedError:
    """
    Структура распарсенной ошибки.

    message_key — i18n-ключ основного сообщения, или None если не распознано.
    raw_message — оригинальный текст, fallback когда message_key=None.
    action_key — i18n-ключ для кнопки действия, или None.
    action_id — машинный ID действия (для обработчика в UI).
    """
    message_key: Optional[str] = None
    raw_message: str = ""
    action_key: Optional[str] = None
    action_id: Optional[str] = None


class ErrorParser:
    """
    Преобразует сырой текст RPC/контрактной ошибки в ParsedError.

    Распознаёт:
    - Сетевые ошибки: insufficient funds, nonce conflict, timeout
    - Контрактные revert: NotWhitelisted, AlreadyVoted, CandidateNotFound,
      InvalidStage, Unauthorized
    - Произвольные revert ("execution reverted: ...")
    - Не распознанное — возвращает raw_message и message_key=None
    """

    def parse(self, error_text: str) -> ParsedError:
        lowered = error_text.lower()

        # ── Сетевые / RPC ошибки ───────────────────────────
        if "insufficient funds" in lowered:
            return ParsedError(
                message_key="err.parser.insufficient_funds",
                raw_message=error_text,
                action_key="err.parser.action.fund",
                action_id="fund_account",
            )

        if "nonce too low" in lowered or "already known" in lowered:
            return ParsedError(
                message_key="err.parser.nonce_conflict",
                raw_message=error_text,
                action_key="err.parser.action.sync_nonce",
                action_id="sync_nonce",
            )

        if "timeout" in lowered or "timed out" in lowered:
            return ParsedError(
                message_key="err.parser.timeout",
                raw_message=error_text,
                action_key="err.parser.action.check_status",
                action_id="check_status",
            )

        # ── Ошибки контракта ───────────────────────────────
        # Распознаём как сырые custom error names,
        # так и тексты от _humanize_contract_error
        if "notwhitelisted" in lowered or "not in the whitelist" in lowered:
            return ParsedError(
                message_key="err.parser.not_whitelisted",
                raw_message=error_text,
            )

        if "alreadyvoted" in lowered or "already voted" in lowered:
            return ParsedError(
                message_key="err.parser.already_voted",
                raw_message=error_text,
            )

        if (
            "candidatenotfound" in lowered
            or "not registered" in lowered
        ):
            return ParsedError(
                message_key="err.parser.candidate_not_found",
                raw_message=error_text,
            )

        if "invalidstage" in lowered or "current stage" in lowered:
            return ParsedError(
                message_key="err.parser.invalid_stage",
                raw_message=error_text,
            )

        if (
            "unauthorized" in lowered
            or "only the contract owner" in lowered
        ):
            return ParsedError(
                message_key="err.parser.unauthorized",
                raw_message=error_text,
            )

        if "execution reverted" in lowered:
            return ParsedError(
                message_key="err.parser.contract_reverted",
                raw_message=error_text,
            )

        # ── Нераспознанная ошибка ──────────────────────────
        return ParsedError(
            message_key=None,
            raw_message=error_text,
        )