"""
Вкладка логов — просмотр session.log.

Toolbar: Refresh | Copy | Save | Clear.
Поиск, автопрокрутка, инфо-строка (Lines | Size | Path).
"""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.ui.widgets.msgbox_helpers import error_ok
from src.ui.widgets.toast import Toast
from src.utils.i18n import t
from src.utils.logger import get_logger
from src.utils.paths import SESSION_LOG

logger = get_logger(__name__)

_ICON_SIZE = QSize(15, 15)


def _icon(name: str, color: str):
    if _QTA:
        return qta.icon(name, color=color)
    from PyQt6.QtGui import QIcon
    return QIcon()


def _format_size(size_bytes: int) -> str:
    """Форматирует размер файла в Б/КБ/МБ."""
    if size_bytes < 1024:
        return t("logs.size_bytes", n=size_bytes)
    elif size_bytes < 1024 * 1024:
        kb = size_bytes / 1024
        return t("logs.size_kb", n=f"{kb:.1f}")
    else:
        mb = size_bytes / (1024 * 1024)
        return t("logs.size_mb", n=f"{mb:.2f}")


class LogsTab(QWidget):
    """Просмотр session.log с фильтрацией и автопрокруткой."""

    def __init__(self) -> None:
        super().__init__()
        self._autoscroll = True
        self._original_text = ""  # для фильтрации поиском
        self._build_ui()
        self._load_log()

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # ── Header: title only ────────────────────────────────
        header = QHBoxLayout()
        title = QLabel(t("logs.title"))
        title.setObjectName("logsTitle")
        self._title_lbl = title
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # ── Toolbar: buttons + search + autoscroll ────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Порядок по ТЗ: Refresh, Copy, Save, Clear
        self._refresh_btn = self._make_btn(
            t("logs.btn.refresh"),
            "fa5s.sync-alt", "#79c0ff",
            t("logs.tooltip.refresh"),
            self._load_log,
        )
        toolbar.addWidget(self._refresh_btn)

        self._copy_btn = self._make_btn(
            t("logs.btn.copy"),
            "fa5s.copy", "#79c0ff",
            t("logs.tooltip.copy"),
            self._copy_log,
        )
        toolbar.addWidget(self._copy_btn)

        self._save_btn = self._make_btn(
            t("logs.btn.save"),
            "fa5s.save", "#3fb950",
            t("logs.tooltip.save"),
            self._save_log,
        )
        toolbar.addWidget(self._save_btn)

        self._clear_btn = self._make_btn(
            t("logs.btn.clear"),
            "fa5s.eraser", "#f85149",
            t("logs.tooltip.clear"),
            self._clear_display,
        )
        toolbar.addWidget(self._clear_btn)

        toolbar.addStretch()

        # Search
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(
            t("logs.search.placeholder")
        )
        self._search_input.setFixedWidth(220)
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(
            self._on_search_changed
        )
        toolbar.addWidget(self._search_input)

        # Autoscroll
        self._autoscroll_cb = QCheckBox(t("logs.autoscroll"))
        self._autoscroll_cb.setChecked(True)
        self._autoscroll_cb.setToolTip(
            t("logs.tooltip.autoscroll")
        )
        self._autoscroll_cb.stateChanged.connect(
            self._on_autoscroll_changed
        )
        toolbar.addWidget(self._autoscroll_cb)

        layout.addLayout(toolbar)

        # ── Log viewer ─────────────────────────────────────────
        self._log_viewer = QTextEdit()
        self._log_viewer.setReadOnly(True)
        self._log_viewer.setObjectName("logsViewer")
        layout.addWidget(self._log_viewer, 1)

        # ── Bottom info: Lines | Size | Path ───────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        self._info_lines_label = QLabel(t("logs.lines", n=0))
        self._info_lines_label.setObjectName("logsCountLabel")
        info_row.addWidget(self._info_lines_label)

        sep1 = QLabel("|")
        sep1.setObjectName("logsCountLabel")
        info_row.addWidget(sep1)

        self._info_size_label = QLabel(
            f"{t('logs.info.size')}: --"
        )
        self._info_size_label.setObjectName("logsCountLabel")
        info_row.addWidget(self._info_size_label)

        sep2 = QLabel("|")
        sep2.setObjectName("logsCountLabel")
        info_row.addWidget(sep2)

        self._info_path_label = QLabel(
            f"{t('logs.info.path')}: {SESSION_LOG}"
        )
        self._info_path_label.setObjectName("logsPathLabel")
        self._info_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        info_row.addWidget(self._info_path_label, 1)

        layout.addLayout(info_row)

    # ─────────────────────────────────────────────────────────────
    def _make_btn(
        self, text, icon_name, color, tooltip, callback
    ) -> QPushButton:
        btn = QPushButton(" " + text)
        btn.setObjectName("iconButton")
        btn.setIcon(_icon(icon_name, color))
        btn.setIconSize(_ICON_SIZE)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        return btn

    # ─────────────────────────────────────────────────────────────
    def _on_search_changed(self, query: str) -> None:
        """Live-фильтр по строкам."""
        if not query:
            self._render_text(self._original_text)
            return
        q = query.lower()
        filtered = "\n".join(
            line for line in self._original_text.splitlines()
            if q in line.lower()
        )
        self._render_text(filtered)

    def _on_autoscroll_changed(self, state: int) -> None:
        self._autoscroll = bool(state)

    def _render_text(self, text: str) -> None:
        """Рендерит текст в QTextEdit и обновляет инфо-строку."""
        self._log_viewer.setPlainText(text)
        self._update_info(text)
        if self._autoscroll:
            scrollbar = self._log_viewer.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _update_info(self, text: str) -> None:
        """Обновляет нижнюю инфо-строку (Lines / Size)."""
        if not text or text == t("logs.not_found"):
            self._info_lines_label.setText(t("logs.lines", n=0))
            self._info_size_label.setText(
                f"{t('logs.info.size')}: --"
            )
            return

        lines = text.count("\n") + (
            1 if text and not text.endswith("\n") else 0
        )
        self._info_lines_label.setText(t("logs.lines", n=lines))

        try:
            if SESSION_LOG.exists():
                size_bytes = SESSION_LOG.stat().st_size
                self._info_size_label.setText(
                    f"{t('logs.info.size')}: {_format_size(size_bytes)}"
                )
            else:
                self._info_size_label.setText(
                    f"{t('logs.info.size')}: --"
                )
        except Exception:
            self._info_size_label.setText(
                f"{t('logs.info.size')}: --"
            )

    # ─────────────────────────────────────────────────────────────
    def _load_log(self) -> None:
        """Загружает session.log и сбрасывает фильтр поиска."""
        try:
            if SESSION_LOG.exists():
                self._original_text = SESSION_LOG.read_text(
                    encoding="utf-8"
                )
            else:
                self._original_text = t("logs.not_found")
        except Exception as exc:
            self._original_text = f"Error reading log:\n{exc}"

        # Если есть активный поиск — применить фильтр заново
        query = self._search_input.text()
        if query:
            self._on_search_changed(query)
        else:
            self._render_text(self._original_text)

    def _save_log(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, t("logs.btn.save"), "session.log",
            "Log Files (*.log);;Text Files (*.txt)",
        )
        if not path:
            return
        try:
            content = self._log_viewer.toPlainText()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            Toast(self, t("logs.toast.saved"), kind="success")
        except Exception as exc:
            error_ok(self, t("common.error"), str(exc))

    def _copy_log(self) -> None:
        content = self._log_viewer.toPlainText()
        if content:
            QApplication.clipboard().setText(content)
            Toast(self, t("logs.toast.copied"), kind="info")

    def _clear_display(self) -> None:
        """Очищает отображение (файл не трогает)."""
        self._log_viewer.clear()
        self._original_text = ""
        self._search_input.clear()
        self._update_info("")

    # ─────────────────────────────────────────────────────────────
    def reset_ui(self) -> None:
        """Сброс для новой сессии."""
        self._log_viewer.clear()
        self._original_text = ""
        self._search_input.clear()
        self._update_info("")
        QTimer.singleShot(500, self._load_log)

    # ─────────────────────────────────────────────────────────────
    # i18n
    # ─────────────────────────────────────────────────────────────
    def retranslate_ui(self) -> None:
        if hasattr(self, "_title_lbl"):
            self._title_lbl.setText(t("logs.title"))

        self._refresh_btn.setText(" " + t("logs.btn.refresh"))
        self._refresh_btn.setToolTip(t("logs.tooltip.refresh"))

        self._copy_btn.setText(" " + t("logs.btn.copy"))
        self._copy_btn.setToolTip(t("logs.tooltip.copy"))

        self._save_btn.setText(" " + t("logs.btn.save"))
        self._save_btn.setToolTip(t("logs.tooltip.save"))

        self._clear_btn.setText(" " + t("logs.btn.clear"))
        self._clear_btn.setToolTip(t("logs.tooltip.clear"))

        self._search_input.setPlaceholderText(
            t("logs.search.placeholder")
        )
        self._autoscroll_cb.setText(t("logs.autoscroll"))
        self._autoscroll_cb.setToolTip(
            t("logs.tooltip.autoscroll")
        )

        # Info-строка обновится через _update_info
        text = self._log_viewer.toPlainText()
        self._update_info(text)
        self._info_path_label.setText(
            f"{t('logs.info.path')}: {SESSION_LOG}"
        )