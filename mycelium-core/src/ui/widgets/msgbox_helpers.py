"""
Хелперы для показа диалогов сообщений.

Last Hotfix: реализованы через MessageDialog (единый виджет).
API совместим с первой версией софта — все вызовы продолжают работать.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QWidget

from src.ui.widgets.message_dialog import MessageDialog


def question_yn(
    parent: QWidget,
    title: str,
    text: str,
    default_no: bool = True,
) -> bool:
    """Вопрос Да/Нет. True если выбрано Да."""
    dlg = MessageDialog(
        parent,
        kind="question",
        title=title,
        text=text,
        buttons=[("common.yes", "yes"), ("common.no", "no")],
        default_button_id="no" if default_no else "yes",
    )
    dlg.exec()
    return dlg.result_id == "yes"


def info_ok(parent: QWidget, title: str, text: str) -> None:
    MessageDialog(
        parent,
        kind="info",
        title=title,
        text=text,
        buttons=[("common.ok", "ok")],
        default_button_id="ok",
    ).exec()


def warning_ok(parent: QWidget, title: str, text: str) -> None:
    MessageDialog(
        parent,
        kind="warning",
        title=title,
        text=text,
        buttons=[("common.ok", "ok")],
        default_button_id="ok",
    ).exec()


def error_ok(parent: QWidget, title: str, text: str) -> None:
    MessageDialog(
        parent,
        kind="error",
        title=title,
        text=text,
        buttons=[("common.ok", "ok")],
        default_button_id="ok",
    ).exec()


def success_ok(parent: QWidget, title: str, text: str) -> None:
    MessageDialog(
        parent,
        kind="success",
        title=title,
        text=text,
        buttons=[("common.ok", "ok")],
        default_button_id="ok",
    ).exec()