"""
Главное окно MYCELIUM CORE.

Хедер: Title + правая группа (New Session, Lang, Theme, About, Exit).
Футер: Status, Progress, Stage, Connected, Geth, Client, Block, Contract.
"""
from __future__ import annotations

import traceback

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.core.app_controller import AppController
from src.ui.tabs.admin_tab import AdminTab
from src.ui.tabs.audit_tab import AuditTab
from src.ui.tabs.logs_tab import LogsTab
from src.ui.tabs.vote_tab import VoteTab
from src.ui.widgets.about_dialog import AboutDialog
from src.ui.widgets.status_badge import StatusBadge
from src.ui.widgets.toast import Toast
from src.ui.widgets.msgbox_helpers import question_yn
from src.ui.workers.thread_runner import ThreadRunner
from src.utils.config import get_app_config
from src.utils.i18n import get_i18n, t
from src.utils.logger import get_logger
from src.ui.widgets.reset_chain_dialog import ResetChainDialog
from src.ui.widgets.startup_warn_dialog import StartupWarnDialog
from src.ui.workers.reset_blockchain_worker import ResetBlockchainWorker


logger = get_logger(__name__)

ICON_SIZE = QSize(15, 15)


def _icon(name: str, color: str):
    if _QTA:
        return qta.icon(name, color=color)
    from PyQt6.QtGui import QIcon
    return QIcon()


class MainWindow(QMainWindow):
    candidates_registered = pyqtSignal()
    stageChanged = pyqtSignal(str)  # SETUP / ACTIVE / FINISHED

    def __init__(self, controller: AppController) -> None:
        super().__init__()
        self.controller = controller
        self.thread_runner = ThreadRunner()

        self.setWindowTitle("MYCELIUM CORE")

        # Иконка окна
        from PyQt6.QtGui import QIcon
        from src.utils.paths import BUNDLE_DIR
        icon_path = BUNDLE_DIR / "src" / "assets" / "icons" / "Original.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setMinimumSize(1100, 700)

        self.controller.set_crash_ui_callback(
            self._on_geth_crash
        )
        self._first_deploy_hint_shown = False
        self._last_stage = None
        # Сигнал crash подключаем, чтобы доставка шла в UI-тред
        self._crash_signal.connect(self._show_crash_dialog)

        self._build_ui()
        self._connect_signals()
        self._start_status_timer()

        # Предупреждение при старте (отложенно — после показа окна)
        QTimer.singleShot(1500, self._check_startup_chain_size)

        # i18n
        get_i18n().languageChanged.connect(
            self._on_language_signal
        )

    # ──────────────────────────────────────────────────────────────
    def _connect_signals(self) -> None:
        self.candidates_registered.connect(
            self.vote_tab.on_candidates_registered
        )
        self.stageChanged.connect(self.admin_tab.on_stage_changed)
        self.stageChanged.connect(self.audit_tab.on_stage_changed)
        self.tabs.currentChanged.connect(
            self._on_tab_changed
        )

    def _on_tab_changed(self, index: int) -> None:
        """
        При переключении табов ничего автоматически не перезагружаем.
        Logs обновляется по кнопке Refresh пользователем.
        """
        pass
    # ──────────────────────────────────────────────────────────────
    # UI Build
    # ──────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Хедер
        header = self._build_header()
        root_layout.addWidget(header)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setObjectName("mainTabs")

        self.admin_tab = AdminTab(self.controller)
        self.vote_tab = VoteTab(self.controller)
        self.audit_tab = AuditTab(self.controller)
        self.logs_tab = LogsTab()

        self.tabs.addTab(self.admin_tab, " " + t("tabs.admin") + " ")
        self.tabs.addTab(self.vote_tab, " " + t("tabs.vote") + " ")
        self.tabs.addTab(self.audit_tab, " " + t("tabs.audit") + " ")
        self.tabs.addTab(self.logs_tab, " " + t("tabs.logs") + " ")

        if _QTA:
            self.tabs.setTabIcon(
                0,
                qta.icon("fa5s.user-shield", color="#388bfd"),
            )
            self.tabs.setTabIcon(
                1,
                qta.icon("fa5s.vote-yea", color="#3fb950"),
            )
            self.tabs.setTabIcon(
                2,
                qta.icon("fa5s.chart-bar", color="#a78bfa"),
            )
            self.tabs.setTabIcon(
                3,
                qta.icon("fa5s.scroll", color="#e3b341"),
            )
            self.tabs.setIconSize(QSize(14, 14))

        root_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(root)

        # Футер (статусбар)
        self._build_statusbar()

    # ──────────────────────────────────────────────────────────────
    # Хедер: только Title + правая группа кнопок
    # ──────────────────────────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(44)
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(6)

        # ── Заголовок ────────────────────────────────────────────────
        title = QLabel(" " + t("header.title"))
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        layout.addStretch()

        # ── Новая сессия ─────────────────────────────────────────
        self.new_session_button = QPushButton(
            " " + t("header.new_session")
        )
        self.new_session_button.setObjectName("iconButton")
        if _QTA:
            self.new_session_button.setIcon(
                _icon("fa5s.redo-alt", "#79c0ff")
            )
            self.new_session_button.setIconSize(ICON_SIZE)
        self.new_session_button.clicked.connect(
            self._new_session
        )
        layout.addWidget(self.new_session_button)

        # Сброс блокчейна
        self.reset_chain_button = QPushButton(
            " " + t("header.reset_chain")
        )
        self.reset_chain_button.setObjectName("iconButton")
        if _QTA:
            self.reset_chain_button.setIcon(
                _icon("fa5s.trash-alt", "#f85149")
            )
            self.reset_chain_button.setIconSize(ICON_SIZE)
        self.reset_chain_button.setToolTip(
            t("header.reset_chain_tooltip")
        )
        self.reset_chain_button.clicked.connect(
            self._reset_blockchain
        )
        layout.addWidget(self.reset_chain_button)

        # ── Выбор языка ──────────────────────────────────────
        lang_icon_lbl = QLabel()
        if _QTA:
            lang_icon_lbl.setPixmap(
                qta.icon(
                    "fa5s.globe", color="#79c0ff"
                ).pixmap(QSize(14, 14))
            )
        layout.addWidget(lang_icon_lbl)

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("EN", "en")
        self._lang_combo.addItem("RU", "ru")
        self._lang_combo.setFixedWidth(60)
        self._lang_combo.setToolTip(t("header.lang_tooltip"))

        cfg = get_app_config()
        idx = self._lang_combo.findData(cfg.language)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(
            self._on_language_changed
        )
        layout.addWidget(self._lang_combo)

        # ── Тема (только иконка) ──────────────────────────────────
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("iconButton")
        if _QTA:
            self.theme_button.setIcon(
                qta.icon("fa5s.adjust", color="#79c0ff")
            )
            self.theme_button.setIconSize(ICON_SIZE)
        self.theme_button.setToolTip(t("header.theme_tooltip"))
        self.theme_button.setFixedWidth(38)
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        # ── О программе (только иконка) ──────────────────────────────
        self.about_button = QPushButton()
        self.about_button.setObjectName("iconButton")
        if _QTA:
            self.about_button.setIcon(
                _icon("fa5s.info-circle", "#79c0ff")
            )
            self.about_button.setIconSize(ICON_SIZE)
        self.about_button.setToolTip(t("header.about_tooltip"))
        self.about_button.setFixedWidth(38)
        self.about_button.clicked.connect(self._show_about)
        layout.addWidget(self.about_button)

        # ── Выход (только иконка) ────────────────────────────────────
        self.exit_button = QPushButton()
        self.exit_button.setObjectName("iconButton")
        if _QTA:
            self.exit_button.setIcon(
                _icon("fa5s.sign-out-alt", "#f85149")
            )
            self.exit_button.setIconSize(ICON_SIZE)
        self.exit_button.setToolTip(t("header.exit_tooltip"))
        self.exit_button.setFixedWidth(38)
        self.exit_button.clicked.connect(self._exit_app)
        layout.addWidget(self.exit_button)

        return header

    # ──────────────────────────────────────────────────────────────
    # Footer: всё информационное
    # ──────────────────────────────────────────────────────────────
    def _build_statusbar(self) -> None:
        bar = QStatusBar()
        bar.setSizeGripEnabled(False)

        # ── Статус ────────────────────────────────────────────
        self._lbl_status = QLabel(t("footer.status") + ":")
        self._lbl_status.setObjectName("fieldLabel")
        bar.addWidget(self._lbl_status)

        self.status_label = QLabel(t("common.ready"))
        self.status_label.setObjectName("statusValue")
        bar.addWidget(self.status_label)

        bar.addWidget(_vsep())

        # ── Прогресс-бар ──────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setObjectName("mainProgressBar")
        bar.addWidget(self.progress_bar)

        bar.addWidget(_vsep())

        # ── Стадия ──────────────────────────────────────────────
        self._lbl_stage = QLabel(t("footer.stage") + ":")
        self._lbl_stage.setObjectName("fieldLabel")
        bar.addWidget(self._lbl_stage)

        self.stage_badge = StatusBadge("SETUP")
        bar.addWidget(self.stage_badge)

        bar.addWidget(_vsep())

        # ── Подключение ────────────────────────────────
        self.rpc_badge = StatusBadge("OFFLINE")
        bar.addWidget(self.rpc_badge)

        bar.addWidget(_vsep())

        # ── Режим Geth ──────────────────────────────────────────
        self._lbl_geth = QLabel(t("footer.geth") + ":")
        self._lbl_geth.setObjectName("fieldLabel")
        bar.addWidget(self._lbl_geth)

        self.geth_mode_badge = StatusBadge("--")
        bar.addWidget(self.geth_mode_badge)

        bar.addWidget(_vsep())

        # ── Клиент ─────────────────────────────────────────────
        self.client_label = QLabel(
            t("footer.client") + ": --"
        )
        self.client_label.setObjectName("fieldLabel")
        bar.addWidget(self.client_label)
        bar.addWidget(_vsep())

        # ── Блок ──────────────────────────────────────────────
        if _QTA:
            block_icon = QLabel()
            block_icon.setPixmap(
                qta.icon(
                    "fa5s.cubes", color="#8b949e"
                ).pixmap(QSize(13, 13))
            )
            bar.addWidget(block_icon)

        self.block_label = QLabel(
            t("footer.block") + ": --"
        )
        self.block_label.setObjectName("fieldLabel")
        bar.addWidget(self.block_label)

        # ── Контракт (постоянный, справа) ───────────────────────
        if _QTA:
            contract_icon = QLabel()
            contract_icon.setPixmap(
                qta.icon(
                    "fa5s.file-contract", color="#8b949e"
                ).pixmap(QSize(13, 13))
            )
            bar.addPermanentWidget(contract_icon)

        self.contract_label = QLabel(
            t("footer.contract_not_deployed")
        )
        self.contract_label.setObjectName("contractLabel")
        self.contract_label.setMaximumWidth(220)
        self.contract_label.setMinimumWidth(80)
        self.contract_label.setTextFormat(
            Qt.TextFormat.PlainText
        )
        bar.addPermanentWidget(self.contract_label)

        self.setStatusBar(bar)

    # ──────────────────────────────────────────────────────────────
    # API прогресс-бара
    # ──────────────────────────────────────────────────────────────
    def show_progress(self, value: int = 0) -> None:
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)

    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(min(value, 100))

    def hide_progress(self) -> None:
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def connect_worker_progress(self, worker) -> None:
        self.show_progress(0)
        worker.percent.connect(self.update_progress)
        worker.finished.connect(
            lambda _: self._on_worker_done()
        )
        worker.error.connect(
            lambda _: self._on_worker_done()
        )

    def _on_worker_done(self) -> None:
        QTimer.singleShot(800, self.hide_progress)

    # ──────────────────────────────────────────────────────────────
    # Сигналы для вкладок
    # ──────────────────────────────────────────────────────────────
    def notify_candidates_registered(self) -> None:
        self.candidates_registered.emit()

    def notify_first_deploy(self) -> None:
        if not self._first_deploy_hint_shown:
            self._first_deploy_hint_shown = True
            QTimer.singleShot(
                2000,
                lambda: Toast(
                    self,
                    t("main.toast.first_deploy_hint"),
                    kind="info",
                ),
            )

    # ──────────────────────────────────────────────────────────────
    # Опрос статуса
    # ──────────────────────────────────────────────────────────────
    def _start_status_timer(self) -> None:
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_status)
        self._timer.start(2000)

    def _refresh_status(self) -> None:
        try:
            connected = self.controller.get_rpc_status()
            self.rpc_badge.setText(
                t("footer.connected")
                if connected
                else t("footer.offline")
            )

            try:
                mode = self.controller.get_geth_mode()
                self.geth_mode_badge.setText(mode.upper())
            except Exception:
                self.geth_mode_badge.setText("--")

            block = self.controller.get_block_number()
            self.block_label.setText(
                f"{t('footer.block')}: {block}"
                if block is not None
                else t("footer.block") + ": --"
            )

            try:
                client = self.controller.get_client_version()
                short = (
                    client[:20] + "..."
                    if len(client) > 20
                    else client
                )
                self.client_label.setText(
                    f"{t('footer.client')}: {short}"
                )
            except Exception:
                pass

            contract = self.controller.get_contract_address()
            if contract:
                # Формат: "Contract: 0x1234...abcd"
                # prefix = "Contract: 0x" + первые 6 hex chars
                # suffix = последние 4 hex chars
                # middle Qt elide
                prefix = contract[:10]   # "0x1234567"
                suffix = contract[-6:]   # "89abcd"
                label_text = (
                    f"{t('footer.contract')}: "
                    f"{prefix}...{suffix}"
                )
                self.contract_label.setText(label_text)
                self.contract_label.setToolTip(
                    f"{t('footer.contract')}: {contract}"
                )
            else:
                self.contract_label.setText(
                    t("footer.contract_not_deployed")
                )
                self.contract_label.setToolTip("")

            try:
                stage = self.controller.get_stage()
                self.stage_badge.setText(stage.name)
                if stage.name != self._last_stage:
                    self._last_stage = stage.name
                    self.stageChanged.emit(stage.name)
            except Exception:
                pass

        except Exception:
            logger.debug(
                "Status refresh error:\n%s",
                traceback.format_exc(),
            )

    # ──────────────────────────────────────────────────────────────
    # Действия
    # ──────────────────────────────────────────────────────────────
    def _toggle_theme(self) -> None:
        app = self.window().app
        current = getattr(app, "_theme_mode", "dark")
        nxt = "light" if current == "dark" else "dark"
        app.theme_manager.apply_theme(nxt)
        app._theme_mode = nxt
        cfg = get_app_config()
        cfg.theme = nxt
        cfg.save()

        # Обновить все StatusBadge — они зависят от темы
        self._refresh_all_status_badges()

    def _refresh_all_status_badges(self) -> None:
        """
        Перерисовывает все StatusBadge с учётом новой темы.
        Палитра бейджей хранится в самом виджете и при смене темы
        нужно её перевычислить.
        """
        from src.ui.widgets.status_badge import StatusBadge
        for badge in self.findChildren(StatusBadge):
            try:
                badge.refresh_theme()
            except Exception:
                pass

    def _show_about(self) -> None:
        """Открывает диалог About."""
        dlg = AboutDialog(self)
        dlg.exec()

    # i18n: handler выбора в combo
    def _on_language_changed(self, index: int) -> None:
        lang = self._lang_combo.itemData(index)
        if not lang:
            return
        cfg = get_app_config()
        cfg.language = lang
        cfg.save()
        try:
            get_i18n().load(lang)
        except Exception as exc:
            logger.warning("Language switch failed: %s", exc)

    # i18n: slot на сигнал I18N.languageChanged
    def _on_language_signal(self, lang: str) -> None:
        try:
            self._retranslate_ui()
            Toast(
                self,
                t("toast.lang_changed_restart"),
                kind="warning",
            )
        except Exception as exc:
            logger.warning("Retranslate failed: %s", exc)

    def _retranslate_ui(self) -> None:
        """Переводит все статические надписи MainWindow + каскад в вкладки."""
        # Хедер
        self.new_session_button.setText(
            " " + t("header.new_session")
        )
        if hasattr(self, "reset_chain_button"):
            self.reset_chain_button.setText(
                " " + t("header.reset_chain")
            )
            self.reset_chain_button.setToolTip(
                t("header.reset_chain_tooltip")
            )
        self.theme_button.setToolTip(t("header.theme_tooltip"))
        self.exit_button.setToolTip(t("header.exit_tooltip"))
        self._lang_combo.setToolTip(t("header.lang_tooltip"))
        self.about_button.setToolTip(t("header.about_tooltip"))

        # Футер
        self._lbl_status.setText(t("footer.status") + ":")
        self._lbl_stage.setText(t("footer.stage") + ":")
        self._lbl_geth.setText(t("footer.geth") + ":")
        if self.status_label.text() in (
            "Ready", "Готов",
        ):
            self.status_label.setText(t("common.ready"))

        # Client / Block / Contract labels — обновятся через _refresh_status

        # Tabs
        self.tabs.setTabText(0, " " + t("tabs.admin") + " ")
        self.tabs.setTabText(1, " " + t("tabs.vote") + " ")
        self.tabs.setTabText(2, " " + t("tabs.audit") + " ")
        self.tabs.setTabText(3, " " + t("tabs.logs") + " ")

        # Каскад на вкладки
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, "retranslate_ui"):
                try:
                    widget.retranslate_ui()
                except Exception as exc:
                    logger.warning(
                        "Tab %d retranslate failed: %s", i, exc
                    )

    def _reset_blockchain(self) -> None:
        """Открывает диалог подтверждения и запускает сброс."""
        active = self.thread_runner.active_count()
        if active > 0:
            from src.ui.widgets.msgbox_helpers import warning_ok
            warning_ok(
                self, t("dialog.active_ops.title"),
                t("dialog.active_ops.msg", count=active),
            )
            return

        try:
            stats = self.controller.get_chain_stats()
        except Exception as exc:
            logger.error("Failed to get chain stats: %s", exc)
            stats = {}

        dlg = ResetChainDialog(self, stats)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if not dlg.confirmed:
            return

        self.reset_chain_button.setEnabled(False)
        self.new_session_button.setEnabled(False)

        self._reset_worker = ResetBlockchainWorker(
            self.controller,
            delete_logs=dlg.delete_logs,
        )
        self._reset_worker.finished.connect(
            self._on_reset_success
        )
        self._reset_worker.error.connect(
            self._on_reset_error
        )
        self.connect_worker_progress(self._reset_worker)
        self._reset_thread = self.thread_runner.start_worker(
            self._reset_worker
        )

    def _on_reset_success(self, _) -> None:
        try:
            self.reset_chain_button.setEnabled(True)
            self.new_session_button.setEnabled(True)

            # Сбросить UI всех вкладок
            self.admin_tab.reset_ui()
            self.vote_tab.reset_ui()
            self.audit_tab.reset_ui()
            self.logs_tab.reset_ui()
            self.contract_label.setText(
                t("footer.contract_not_deployed")
            )
            self.stage_badge.setText("SETUP")
            self.status_label.setText(t("common.ready"))

            Toast(self, t("reset.toast.success"), kind="success")
        except Exception as exc:
            logger.error("UI update after reset failed: %s", exc)

    def _on_reset_error(self, error: str) -> None:
        try:
            self.reset_chain_button.setEnabled(True)
            self.new_session_button.setEnabled(True)
            logger.error("Blockchain reset failed: %s", error)

            from src.ui.widgets.msgbox_helpers import error_ok

            # Спец-случай: файлы залочены, нужна ручная очистка
            if str(error).startswith("MANUAL_CLEANUP_REQUIRED|"):
                paths = str(error).split("|", 1)[1]
                error_ok(
                    self,
                    t("reset.dialog.manual_title"),
                    t("reset.dialog.manual_msg", paths=paths),
                )
            else:
                error_ok(self, t("reset.toast.failed"), str(error))
        except Exception:
            pass

    def _check_startup_chain_size(self) -> None:
        """
        Проверяет размер chain-data при старте.
        Если > 500 МБ и пользователь не выключил предупреждение —
        показывает диалог.
        """
        cfg = get_app_config()
        if cfg.get_bool(
            "startup", "warn_chain_size_shown", fallback=False
        ):
            return

        try:
            stats = self.controller.get_chain_stats()
            size_mb = stats.get("size_mb", 0)
        except Exception:
            return

        if size_mb < 500:
            return

        dlg = StartupWarnDialog(self, size_mb)
        dlg.exec()

        if dlg.dont_show_again:
            cfg.set(
                "startup", "warn_chain_size_shown", "true"
            )
            cfg.save()

    def _new_session(self) -> None:
        active = self.thread_runner.active_count()
        if active > 0:
            from src.ui.widgets.msgbox_helpers import warning_ok
            warning_ok(
                self, t("dialog.active_ops.title"),
                t("dialog.active_ops.msg", count=active),
            )
            return

        cfg = get_app_config()
        auto = cfg.get_bool(
            "session", "auto_deploy_on_reset", fallback=False
        )
        dlg = _NewSessionDialog(self, auto)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        cfg.set(
            "session", "auto_deploy_on_reset",
            str(dlg.auto_deploy).lower(),
        )
        cfg.save()

        logger.info("User initiated new session")
        self.controller.new_session()

        self.admin_tab.reset_ui()
        self.vote_tab.reset_ui()
        self.audit_tab.reset_ui()
        self.logs_tab.reset_ui()
        self.hide_progress()

        self.contract_label.setText(
            t("footer.contract_not_deployed")
        )
        self.stage_badge.setText("SETUP")
        self.status_label.setText(t("common.ready"))

        Toast(self, t("main.toast.new_session"), kind="success")

        if dlg.auto_deploy:
            key = (
                self.admin_tab.admin_key_input.text().strip()
            )
            if key:
                QTimer.singleShot(
                    500, self.admin_tab._deploy_contract
                )
            else:
                Toast(
                    self,
                    t("main.toast.auto_deploy_skipped"),
                    kind="warning",
                )

    def _exit_app(self) -> None:
        self.close()

    # ──────────────────────────────────────────────────────────────
    # Аварийная остановка Geth
    # ──────────────────────────────────────────────────────────────
    # Сигнал для thread-safe доставки crash-нотификации в UI-тред
    _crash_signal = pyqtSignal()

    def _on_geth_crash(self) -> None:
        """Вызывается из monitor-треда Geth. Перенаправляет в UI-тред через сигнал."""
        try:
            self._crash_signal.emit()
        except Exception:
            pass

    @pyqtSlot()
    def _show_crash_dialog(self) -> None:
        from src.ui.widgets.msgbox_helpers import error_ok
        error_ok(
            self,
            t("dialog.crash.title"),
            t("dialog.crash.msg"),
        )

    # ──────────────────────────────────────────────────────────────
    # Событие закрытия — принудительное завершение Geth
    # ──────────────────────────────────────────────────────────────
    def closeEvent(self, event) -> None:
        active = self.thread_runner.active_count()
        if active > 0:
            if not question_yn(
                self,
                t("dialog.active_ops.title"),
                t("dialog.active_ops.msg", count=active),
            ):
                event.ignore()
                return
        else:
            if not question_yn(
                self,
                t("dialog.exit.title"),
                t("dialog.exit.msg"),
            ):
                event.ignore()
                return

        try:
            self._timer.stop()
        except Exception:
            pass

        try:
            self.controller.shutdown()
        except Exception:
            logger.exception("Error during shutdown")

        super().closeEvent(event)

# ──────────────────────────────────────────────────────────────────
# Диалоги
# ──────────────────────────────────────────────────────────────────
class _NewSessionDialog(QDialog):
    def __init__(self, parent, auto_deploy_default=False):
        super().__init__(parent)
        self.setWindowTitle(t("dialog.new_session.title"))
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        msg = QLabel(t("dialog.new_session.msg"))
        msg.setWordWrap(True)
        layout.addWidget(msg)

        self._auto_deploy_cb = QCheckBox(
            t("dialog.new_session.auto")
        )
        self._auto_deploy_cb.setChecked(auto_deploy_default)
        layout.addWidget(self._auto_deploy_cb)

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton(t("common.cancel"))
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        start_btn = QPushButton(" " + t("dialog.new_session.start"))
        start_btn.setObjectName("deployButton")
        if _QTA:
            start_btn.setIcon(
                _icon("fa5s.redo-alt", "#ffffff")
            )
            start_btn.setIconSize(ICON_SIZE)
        start_btn.clicked.connect(self.accept)
        buttons.addWidget(start_btn)

        layout.addLayout(buttons)

    @property
    def auto_deploy(self):
        return self._auto_deploy_cb.isChecked()

# ──────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ──────────────────────────────────────────────────────────────────
def _vsep() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine)
    sep.setFixedWidth(1)
    sep.setObjectName("headerSep")
    return sep