"""
Вкладка аудита — проверки безопасности и результаты.
"""
from __future__ import annotations

import json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.core.models import ElectionStage
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from src.ui.widgets.msgbox_helpers import error_ok
from src.ui.widgets.status_badge import StatusBadge
from src.ui.widgets.toast import Toast
from src.ui.workers.base_worker import BaseWorker
from src.utils.i18n import t
from src.utils.logger import get_logger

logger = get_logger(__name__)

_ICON_SIZE = QSize(15, 15)


def _icon(name: str, color: str):
    if _QTA:
        return qta.icon(name, color=color)
    from PyQt6.QtGui import QIcon
    return QIcon()


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("fieldLabel")
    return lbl


class AuditTab(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller
        self._last_report = None
        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(self._build_results_section())
        layout.addWidget(self._build_checks_section())
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ─── Results section: ТОЛЬКО результаты + Refresh ──────────
    def _build_results_section(self) -> QGroupBox:
        box = QGroupBox(t("audit.section.results"))
        self._sec_results = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        # Строка победителя
        wr = QHBoxLayout()
        self._lbl_winner = _field_label(t("audit.label.winner"))
        wr.addWidget(self._lbl_winner)

        self._winner_label = QLabel("--")
        self._winner_label.setObjectName("sectionHeader")
        wr.addWidget(self._winner_label)
        wr.addStretch()
        layout.addLayout(wr)

        # Лейбл кандидатов + таблица
        self._lbl_cands = _field_label(t("audit.label.candidates"))
        layout.addWidget(self._lbl_cands)

        self._results_table = QTableWidget(0, 4)
        self._results_table.setHorizontalHeaderLabels([
            t("audit.col.candidate"),
            t("audit.col.party"),
            t("audit.col.address"),
            t("audit.col.votes"),
        ])
        self._results_table.verticalHeader().setVisible(False)
        self._results_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._results_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._results_table.setAlternatingRowColors(True)
        self._results_table.setMinimumHeight(140)
        self._results_table.horizontalHeader()\
            .setHighlightSections(False)
        self._results_table.setColumnWidth(0, 180)
        self._results_table.setColumnWidth(1, 140)
        self._results_table.setColumnWidth(3, 80)
        self._results_table.horizontalHeader()\
            .setSectionResizeMode(
                2, QHeaderView.ResizeMode.Stretch
            )
        layout.addWidget(self._results_table)

        # Только Refresh (Export перенесён в секцию Checks)
        btn_row = QHBoxLayout()
        self._refresh_btn = QPushButton(" " + t("audit.btn.refresh"))
        self._refresh_btn.setObjectName("iconButton")
        self._refresh_btn.setIcon(
            _icon("fa5s.sync-alt", "#79c0ff")
        )
        self._refresh_btn.setIconSize(_ICON_SIZE)
        self._refresh_btn.clicked.connect(self._refresh_results)
        btn_row.addWidget(self._refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return box

    # ─── Security Checks section: run + Copy/JSON/CSV ─────────
    def _build_checks_section(self) -> QGroupBox:
        box = QGroupBox(t("audit.section.checks"))
        self._sec_checks = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        # Выбор режима аудита
        mode_row = QHBoxLayout()
        self._lbl_mode = _field_label(t("audit.label.audit_mode"))
        mode_row.addWidget(self._lbl_mode)

        self._mode_combo = QComboBox()
        self._mode_combo.setMinimumWidth(260)
        self._mode_combo.currentIndexChanged.connect(
            self._on_mode_changed
        )
        mode_row.addWidget(self._mode_combo)

        mode_row.addStretch()

        self._mode_desc = QLabel("")
        self._mode_desc.setObjectName("fieldLabel")
        mode_row.addWidget(self._mode_desc)
        layout.addLayout(mode_row)

        # Кнопка запуска аудита
        self._run_btn = QPushButton(" " + t("audit.btn.run"))
        self._run_btn.setObjectName("whitelistButton")
        self._run_btn.setIcon(
            _icon("fa5s.shield-alt", "#3fb950")
        )
        self._run_btn.setIconSize(_ICON_SIZE)
        self._run_btn.clicked.connect(self._run_audit)
        layout.addWidget(self._run_btn)

        # Таблица проверок
        self._lbl_check_results = _field_label(
            t("audit.label.check_results")
        )
        layout.addWidget(self._lbl_check_results)

        self._checks_table = QTableWidget(0, 3)
        self._checks_table.setHorizontalHeaderLabels([
            t("audit.col.check"),
            t("audit.col.status"),
            t("audit.col.details"),
        ])
        self._checks_table.verticalHeader().setVisible(False)
        self._checks_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._checks_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._checks_table.setAlternatingRowColors(True)
        self._checks_table.setMinimumHeight(200)
        self._checks_table.horizontalHeader()\
            .setHighlightSections(False)
        self._checks_table.setColumnWidth(0, 220)
        self._checks_table.setColumnWidth(1, 100)
        self._checks_table.horizontalHeader()\
            .setSectionResizeMode(
                2, QHeaderView.ResizeMode.Stretch
            )
        layout.addWidget(self._checks_table)

        # Итоги + Копировать / JSON / CSV
        action_row = QHBoxLayout()
        self._summary_label = QLabel(t("audit.no_audit"))
        self._summary_label.setObjectName("fieldLabel")
        action_row.addWidget(self._summary_label)
        action_row.addStretch()

        # Порядок: Copy Report | Export JSON | Export CSV
        self._copy_audit_btn = QPushButton(
            " " + t("audit.btn.copy_report")
        )
        self._copy_audit_btn.setObjectName("iconButton")
        self._copy_audit_btn.setIcon(
            _icon("fa5s.copy", "#79c0ff")
        )
        self._copy_audit_btn.setIconSize(_ICON_SIZE)
        self._copy_audit_btn.setEnabled(False)
        self._copy_audit_btn.clicked.connect(self._copy_full_report)
        action_row.addWidget(self._copy_audit_btn)

        self._export_json_btn = QPushButton(" JSON")
        self._export_json_btn.setObjectName("iconButton")
        self._export_json_btn.setIcon(
            _icon("fa5s.file-export", "#e3b341")
        )
        self._export_json_btn.setIconSize(_ICON_SIZE)
        self._export_json_btn.setEnabled(False)
        self._export_json_btn.clicked.connect(self._export_json)
        action_row.addWidget(self._export_json_btn)

        self._export_csv_btn = QPushButton(" CSV")
        self._export_csv_btn.setObjectName("iconButton")
        self._export_csv_btn.setIcon(
            _icon("fa5s.file-csv", "#3fb950")
        )
        self._export_csv_btn.setIconSize(_ICON_SIZE)
        self._export_csv_btn.setEnabled(False)
        self._export_csv_btn.clicked.connect(self._export_csv)
        action_row.addWidget(self._export_csv_btn)

        layout.addLayout(action_row)

        # Заполняем combo ПОСЛЕ создания _run_btn, чтобы
        # _populate_mode_combo мог вызвать _update_run_btn_state
        self._populate_mode_combo()
        self._on_mode_changed(self._mode_combo.currentIndex())
        return box

    # ─────────────────────────────────────────────────────────────
    # Доступность режимов (зависит от стадии)
    # ─────────────────────────────────────────────────────────────
    def _get_current_stage_name(self) -> str | None:
        """Возвращает имя текущей стадии или None."""
        try:
            stage = self.controller.get_stage()
            return stage.name
        except Exception:
            return None

    def _is_mode_available(self, mode_idx: int) -> tuple[bool, str]:
        """
        Возвращает (available, reason_key).
        mode_idx: 0=full, 1=pre, 2=live, 3=final
        """
        stage = self._get_current_stage_name()
        if stage is None:
            return False, "audit.availability.reason.no_session"

        # full и final: только в FINISHED
        if mode_idx in (0, 3):
            if stage == "FINISHED":
                return True, ""
            return False, "audit.availability.reason.not_finished"

        # pre: только в SETUP
        if mode_idx == 1:
            if stage == "SETUP":
                return True, ""
            return False, "audit.availability.reason.not_setup"

        # live: только в ACTIVE
        if mode_idx == 2:
            if stage == "ACTIVE":
                return True, ""
            return False, "audit.availability.reason.not_active"

        return True, ""

    def _populate_mode_combo(self) -> None:
        """
        Заполняет combo с пометками available/unavailable.
        Использует QStandardItemModel чтобы отключать недоступные пункты.
        """
        model = QStandardItemModel()

        mode_keys = [
            "audit.mode.full",
            "audit.mode.pre",
            "audit.mode.live",
            "audit.mode.final",
        ]

        for idx, mode_key in enumerate(mode_keys):
            available, _ = self._is_mode_available(idx)
            suffix_key = (
                "audit.availability.available"
                if available
                else "audit.availability.unavailable"
            )
            text = f"{t(mode_key)}  ({t(suffix_key)})"

            item = QStandardItem(text)
            if not available:
                # Делаем пункт неактивным (нельзя выбрать)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            model.appendRow(item)

        # Сохранить текущий выбор, если он остался доступным
        current_idx = self._mode_combo.currentIndex()
        self._mode_combo.blockSignals(True)
        self._mode_combo.setModel(model)

        # Если текущий пункт стал недоступен — выбрать первый доступный
        if current_idx < 0 or not self._is_mode_available(current_idx)[0]:
            for i in range(4):
                if self._is_mode_available(i)[0]:
                    self._mode_combo.setCurrentIndex(i)
                    break
            else:
                self._mode_combo.setCurrentIndex(0)
        else:
            self._mode_combo.setCurrentIndex(current_idx)
        self._mode_combo.blockSignals(False)

        # Run-кнопка активна только если выбран доступный пункт
        self._update_run_btn_state()

    def _update_run_btn_state(self) -> None:
        """Run кнопка активна только при доступном режиме."""
        idx = self._mode_combo.currentIndex()
        if idx < 0:
            self._run_btn.setEnabled(False)
            return
        available, _ = self._is_mode_available(idx)
        self._run_btn.setEnabled(available)

    def on_stage_changed(self, stage_name: str) -> None:
        """
        Slot для MainWindow.stageChanged.
        Пересобирает combo и обновляет описание.
        """
        self._populate_mode_combo()
        self._on_mode_changed(self._mode_combo.currentIndex())

    # ─────────────────────────────────────────────────────────────
    def _on_mode_changed(self, index: int) -> None:
        keys = {
            0: "audit.desc.full",
            1: "audit.desc.pre",
            2: "audit.desc.live",
            3: "audit.desc.final",
        }
        base_desc = t(keys.get(index, "audit.desc.full"))

        available, reason_key = self._is_mode_available(index)
        if available:
            self._mode_desc.setText(base_desc)
        else:
            reason = t(reason_key) if reason_key else ""
            self._mode_desc.setText(f"{base_desc}  ({reason})")

        self._update_run_btn_state()

    # ─────────────────────────────────────────────────────────────
    # Запуск аудита
    # ─────────────────────────────────────────────────────────────
    def _run_audit(self) -> None:
        mode_map = {0: "full", 1: "pre", 2: "live", 3: "final"}
        mode = mode_map.get(
            self._mode_combo.currentIndex(), "full"
        )

        self._run_btn.setEnabled(False)
        self._checks_table.setRowCount(0)
        self._summary_label.setText(t("audit.running"))

        self._worker = _StagedAuditWorker(
            self.controller, mode
        )
        self._worker.finished.connect(self._on_audit_success)
        self._worker.error.connect(self._on_audit_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._worker)
        self._thread = mw.thread_runner.start_worker(self._worker)

    def _on_audit_success(self, report) -> None:
        self._run_btn.setEnabled(True)
        self._last_report = report

        # Все три кнопки экспорта доступны после успешного аудита
        self._copy_audit_btn.setEnabled(True)
        self._export_json_btn.setEnabled(True)
        self._export_csv_btn.setEnabled(True)

        # Populate checks table
        self._checks_table.setRowCount(0)
        for check in report.checks:
            row = self._checks_table.rowCount()
            self._checks_table.insertRow(row)

            name_item = QTableWidgetItem(check.check_name)
            name_item.setFlags(
                name_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self._checks_table.setItem(row, 0, name_item)

            badge = StatusBadge(check.status)
            self._checks_table.setCellWidget(row, 1, badge)

            detail_item = QTableWidgetItem(check.details)
            detail_item.setFlags(
                detail_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self._checks_table.setItem(row, 2, detail_item)

        ts = report.audit_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self._summary_label.setText(
            t(
                "audit.summary",
                ts=ts,
                passed=report.passed_count,
                failed=report.failed_count,
                total=len(report.checks),
            )
        )

        self._refresh_results()
        Toast(self, t("audit.toast.completed"), kind="success")

    def _on_audit_error(self, error: str) -> None:
        self._run_btn.setEnabled(True)
        self._summary_label.setText(t("audit.failed"))
        error_ok(self, t("audit.failed"), error)

    # ─────────────────────────────────────────────────────────────
    # Копирование / Экспорт — единый источник: build_full_report()
    # ─────────────────────────────────────────────────────────────
    def _copy_full_report(self) -> None:
        """Копирует полный отчёт (результаты + аудит) в JSON-формате."""
        try:
            payload = self.controller.build_full_report()
            text = json.dumps(
                payload, indent=2, ensure_ascii=False, default=str
            )
            QApplication.clipboard().setText(text)
            Toast(self, t("audit.toast.copied"), kind="info")
        except Exception as exc:
            error_ok(self, t("common.error"), str(exc))

    def _export_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, t("audit.export.json_title"), "results.json",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            self.controller.export_results(path)
            Toast(self, t("audit.toast.json_exported"), kind="success")
        except Exception as exc:
            error_ok(self, t("audit.dialog.export_failed"), str(exc))

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, t("audit.export.csv_title"), "results.csv",
            "CSV (*.csv)",
        )
        if not path:
            return
        try:
            self.controller.export_results_csv(path)
            Toast(self, t("audit.toast.csv_exported"), kind="success")
        except Exception as exc:
            error_ok(self, t("audit.dialog.export_failed"), str(exc))

    # ─────────────────────────────────────────────────────────────
    # Результаты
    # ─────────────────────────────────────────────────────────────
    def _refresh_results(self) -> None:
        try:
            results = self.controller.get_results()
            self._results_table.setRowCount(0)
            if not results:
                self._winner_label.setText(t("audit.no_results"))
                return

            for c in results:
                row = self._results_table.rowCount()
                self._results_table.insertRow(row)
                for col, val in enumerate([
                    c.name, c.party, c.address, str(c.vote_count),
                ]):
                    item = QTableWidgetItem(val)
                    item.setFlags(
                        item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )
                    if col == 2:
                        item.setFont(QFont("Consolas", 10))
                    if col == 3:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter
                        )
                    self._results_table.setItem(row, col, item)

            # Winner показывается ТОЛЬКО при FINISHED
            try:
                stage = self.controller.get_stage()
            except Exception:
                stage = None

            if (
                stage is not None
                and stage != ElectionStage.FINISHED
            ):
                self._winner_label.setText(
                    t("audit.winner_after_finish")
                )
                return

            winner = self.controller.get_winner()
            if winner is None:
                self._winner_label.setText(t("audit.no_winner"))
            elif winner["type"] == "tie":
                names = ", ".join(
                    c.name for c in winner["candidates"]
                )
                self._winner_label.setText(
                    t("audit.tie", names=names)
                )
            else:
                c = winner["candidate"]
                self._winner_label.setText(
                    f"{c.name} ({c.party})"
                )
        except Exception as exc:
            self._winner_label.setText(f"Error: {exc}")

    # ─────────────────────────────────────────────────────────────
    # Сброс
    # ─────────────────────────────────────────────────────────────
    def reset_ui(self) -> None:
        self._results_table.setRowCount(0)
        self._checks_table.setRowCount(0)
        self._winner_label.setText("--")
        self._summary_label.setText(t("audit.no_audit"))
        self._run_btn.setEnabled(True)
        self._copy_audit_btn.setEnabled(False)
        self._export_json_btn.setEnabled(False)
        self._export_csv_btn.setEnabled(False)
        self._mode_combo.setCurrentIndex(0)
        self._last_report = None
        logger.info("AuditTab UI reset")

    # ─────────────────────────────────────────────────────────────
    # i18n
    # ─────────────────────────────────────────────────────────────
    def retranslate_ui(self) -> None:
        if hasattr(self, "_sec_results"):
            self._sec_results.setTitle(t("audit.section.results"))
        if hasattr(self, "_sec_checks"):
            self._sec_checks.setTitle(t("audit.section.checks"))

        if hasattr(self, "_lbl_winner"):
            self._lbl_winner.setText(t("audit.label.winner").upper())
        if hasattr(self, "_lbl_cands"):
            self._lbl_cands.setText(t("audit.label.candidates").upper())
        if hasattr(self, "_lbl_mode"):
            self._lbl_mode.setText(t("audit.label.audit_mode").upper())
        if hasattr(self, "_lbl_check_results"):
            self._lbl_check_results.setText(
                t("audit.label.check_results").upper()
            )

        self._refresh_btn.setText(" " + t("audit.btn.refresh"))
        self._run_btn.setText(" " + t("audit.btn.run"))
        self._copy_audit_btn.setText(" " + t("audit.btn.copy_report"))
        # JSON/CSV — без перевода (бренды форматов)

        self._results_table.setHorizontalHeaderLabels([
            t("audit.col.candidate"),
            t("audit.col.party"),
            t("audit.col.address"),
            t("audit.col.votes"),
        ])
        self._checks_table.setHorizontalHeaderLabels([
            t("audit.col.check"),
            t("audit.col.status"),
            t("audit.col.details"),
        ])

        # Mode combo: пересобираем через _populate_mode_combo
        # (он сам учитывает текущую стадию и переводы)
        self._populate_mode_combo()
        self._on_mode_changed(self._mode_combo.currentIndex())

        if self._last_report is None:
            self._summary_label.setText(t("audit.no_audit"))


# ──────────────────────────────────────────────────────────────────
class _StagedAuditWorker(BaseWorker):
    def __init__(self, controller, mode: str) -> None:
        super().__init__()
        self.controller = controller
        self._mode = mode

    def run(self) -> None:
        try:
            self.percent.emit(20)

            sid = self.controller.session.session_id
            db = self.controller.session.deploy_block

            if not sid:
                self.error.emit("No active session")
                return

            svc = self.controller.audit_service
            if self._mode == "pre":
                report = svc.run_pre_vote_audit(sid, db)
            elif self._mode == "live":
                report = svc.run_live_audit(sid, db)
            elif self._mode == "final":
                report = svc.run_final_audit(sid, db)
            else:
                report = svc.run_audit(sid, db)

            self.percent.emit(100)
            self.finished.emit(report)

        except Exception as exc:
            self.error.emit(str(exc))