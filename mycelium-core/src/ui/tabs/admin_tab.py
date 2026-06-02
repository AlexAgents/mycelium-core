"""
Вкладка админа.
"""
from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.ui.widgets.confirm_dialog import ConfirmDialog
from src.ui.widgets.error_dialog import ErrorDialog
from src.ui.widgets.msgbox_helpers import (
    error_ok,
    info_ok,
    question_yn,
    warning_ok,
)
from src.ui.widgets.toast import Toast
from src.ui.workers.deploy_worker import DeployWorker
from src.ui.workers.fund_voters_worker import FundVotersWorker
from src.ui.workers.whitelist_worker import WhitelistWorker
from src.ui.workers.stage_worker import StageWorker
from src.ui.workers.fund_from_dev_worker import FundFromDevWorker
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


class _VoterDropZone(QGroupBox):
    """QGroupBox с drag-and-drop для JSON-файлов."""

    def __init__(self, title: str, parent_tab) -> None:
        super().__init__(title)
        self._parent_tab = parent_tab
        self.setAcceptDrops(True)
        self._drag_active = False

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".json"):
                    event.acceptProposedAction()
                    self._drag_active = True
                    self.setProperty("dragOver", True)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._drag_active = False
        self.setProperty("dragOver", False)
        self.style().polish(self)

    def dropEvent(self, event) -> None:
        self._drag_active = False
        self.setProperty("dragOver", False)
        self.style().polish(self)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".json"):
                self._parent_tab._import_voters_from_path(path)
                event.acceptProposedAction()
                return
        event.ignore()


class AdminTab(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller
        self._staged_candidates: list[tuple[str, str, str]] = []
        self._candidates_registered: bool = False
        self._build_ui()
        self._apply_dev_defaults()

    # ──────────────────────────────────────────────────────────────
    def _apply_dev_defaults(self) -> None:
        if self.controller.is_dev_mode():
            key = self.controller.get_dev_admin_key()
            if key:
                self.admin_key_input.setText(key)
                logger.info("DEV_ADMIN_KEY auto-filled from .env")
                self._refresh_admin_balance()

    # ──────────────────────────────────────────────────────────────
    # UI Build
    # ──────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(self._build_contract_section())
        layout.addWidget(self._build_candidates_section())
        layout.addWidget(self._build_voters_section())
        layout.addWidget(self._build_stage_section())
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)
        # Изначально (до деплоя) — всё что зависит от контракта заблокировано
        self._set_pre_deploy_state()

    # ─── Контракт ──────────────────────────────────────────────
    def _build_contract_section(self) -> QGroupBox:
        box = QGroupBox(t("admin.section.contract"))
        self._sec_contract = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        self._lbl_admin_key = _field_label(t("admin.label.admin_key"))
        layout.addWidget(self._lbl_admin_key)

        key_row = QHBoxLayout()
        self.admin_key_input = QLineEdit()
        self.admin_key_input.setPlaceholderText("0x...")
        self.admin_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        key_row.addWidget(self.admin_key_input)

        self._show_key_btn = QPushButton()
        self._show_key_btn.setObjectName("iconButton")
        self._show_key_btn.setIcon(_icon("fa5s.eye", "#58a6ff"))
        self._show_key_btn.setIconSize(_ICON_SIZE)
        self._show_key_btn.setToolTip(t("admin.tooltip.show_hide"))
        self._show_key_btn.setFixedWidth(32)
        self._show_key_btn.clicked.connect(self._toggle_key_visibility)
        key_row.addWidget(self._show_key_btn)
        layout.addLayout(key_row)

        # Строка баланса: компактное отображение
        bal_row = QHBoxLayout()
        self._lbl_balance = _field_label(t("admin.label.balance"))
        bal_row.addWidget(self._lbl_balance)

        self._admin_balance_label = QLabel("--")
        self._admin_balance_label.setObjectName("monoLabel")
        self._admin_balance_label.setMaximumWidth(180)
        bal_row.addWidget(self._admin_balance_label)

        # Dev-лейбл — отдельный, может скрываться
        self._dev_balance_label = QLabel("")
        self._dev_balance_label.setObjectName("monoLabel")
        self._dev_balance_label.setMaximumWidth(160)
        self._dev_balance_label.setVisible(False)
        bal_row.addWidget(self._dev_balance_label)

        bal_row.addStretch()

        # Кнопка Fund from Dev (только dev-режим)
        self._fund_dev_btn = QPushButton()
        self._fund_dev_btn.setObjectName("iconButton")
        self._fund_dev_btn.setIcon(
            _icon("fa5s.hand-holding-usd", "#e3b341")
        )
        self._fund_dev_btn.setIconSize(_ICON_SIZE)
        self._fund_dev_btn.setToolTip(t("admin.tooltip.fund_from_dev"))
        self._fund_dev_btn.setFixedWidth(32)
        self._fund_dev_btn.clicked.connect(self._fund_admin_from_dev)
        if not self.controller.is_dev_mode():
            self._fund_dev_btn.setVisible(False)
        bal_row.addWidget(self._fund_dev_btn)

        self._refresh_balance_btn = QPushButton()
        self._refresh_balance_btn.setObjectName("iconButton")
        self._refresh_balance_btn.setIcon(_icon("fa5s.sync-alt", "#79c0ff"))
        self._refresh_balance_btn.setIconSize(_ICON_SIZE)
        self._refresh_balance_btn.setToolTip(t("admin.tooltip.refresh_balance"))
        self._refresh_balance_btn.setFixedWidth(32)
        self._refresh_balance_btn.clicked.connect(self._refresh_admin_balance)
        bal_row.addWidget(self._refresh_balance_btn)

        layout.addLayout(bal_row)

        # --- Деплой ---
        self.deploy_button = QPushButton(" " + t("admin.btn.deploy"))
        self.deploy_button.setObjectName("registerCandidatesButton")
        self.deploy_button.setIcon(_icon("fa5s.rocket", "#388bfd"))
        self.deploy_button.setIconSize(_ICON_SIZE)
        self.deploy_button.clicked.connect(self._deploy_contract)
        layout.addWidget(self.deploy_button)

        # --- Адрес контракта ---
        self._lbl_contract_addr = _field_label(t("admin.label.contract_addr"))
        layout.addWidget(self._lbl_contract_addr)

        self.contract_addr_label = QLabel("--")
        self.contract_addr_label.setObjectName("monoLabel")
        self.contract_addr_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.contract_addr_label)

        # --- Отображение стадии ---
        stage_row = QHBoxLayout()
        self._lbl_current_stage = _field_label(t("admin.label.current_stage"))
        stage_row.addWidget(self._lbl_current_stage)
        stage_row.addStretch()
        self.stage_value_label = QLabel("--")
        self.stage_value_label.setObjectName("statusValue")
        stage_row.addWidget(self.stage_value_label)
        layout.addLayout(stage_row)

        self._deploy_log = _make_log_box(3)
        layout.addWidget(self._deploy_log)
        return box

    # ─── Кандидаты ─────────────────────────────────────────────
    def _build_candidates_section(self) -> QGroupBox:
        box = QGroupBox(t("admin.section.candidates"))
        self._sec_candidates = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(10)

        name_col = QVBoxLayout()
        self._lbl_name = _field_label(t("admin.label.name"))
        name_col.addWidget(self._lbl_name)
        self.candidate_name_input = QLineEdit()
        self.candidate_name_input.setPlaceholderText(t("admin.placeholder.name"))
        name_col.addWidget(self.candidate_name_input)
        fields_row.addLayout(name_col)

        party_col = QVBoxLayout()
        self._lbl_party = _field_label(t("admin.label.party"))
        party_col.addWidget(self._lbl_party)
        self.candidate_party_input = QLineEdit()
        self.candidate_party_input.setPlaceholderText(t("admin.placeholder.party"))
        party_col.addWidget(self.candidate_party_input)
        fields_row.addLayout(party_col)

        layout.addLayout(fields_row)

        self._lbl_eth_addr = _field_label(t("admin.label.eth_addr"))
        layout.addWidget(self._lbl_eth_addr)

        addr_row = QHBoxLayout()
        addr_row.setSpacing(6)
        self.candidate_address_input = QLineEdit()
        self.candidate_address_input.setPlaceholderText("0x...")
        self.candidate_address_input.setObjectName("monoLabel")
        addr_row.addWidget(self.candidate_address_input)

        self._cand_gen_btn = QPushButton(" " + t("admin.btn.generate"))
        self._cand_gen_btn.setObjectName("iconButton")
        self._cand_gen_btn.setIcon(_icon("fa5s.magic", "#e3b341"))
        self._cand_gen_btn.setIconSize(_ICON_SIZE)
        self._cand_gen_btn.clicked.connect(self._generate_candidate_address)
        addr_row.addWidget(self._cand_gen_btn)

        self._cand_add_btn = QPushButton(" " + t("admin.btn.add"))
        self._cand_add_btn.setObjectName("iconButton")
        self._cand_add_btn.setIcon(_icon("fa5s.plus", "#3fb950"))
        self._cand_add_btn.setIconSize(_ICON_SIZE)
        self._cand_add_btn.clicked.connect(self._add_candidate_to_list)
        addr_row.addWidget(self._cand_add_btn)

        layout.addLayout(addr_row)

        self._lbl_cands_list = _field_label(t("admin.label.candidates_list"))
        layout.addWidget(self._lbl_cands_list)
        self.candidates_table = _make_table(
            ["Name", "Party", "Address"],
            col_widths=[180, 160, None],
            stretch_col=2, min_height=110,
        )
        layout.addWidget(self.candidates_table)

        btn_row = QHBoxLayout()
        self._cand_rm_btn = QPushButton(" " + t("admin.btn.remove"))
        self._cand_rm_btn.setObjectName("iconButton")
        self._cand_rm_btn.setIcon(_icon("fa5s.trash-alt", "#f85149"))
        self._cand_rm_btn.setIconSize(_ICON_SIZE)
        self._cand_rm_btn.clicked.connect(self._remove_selected_candidate)
        btn_row.addWidget(self._cand_rm_btn)
        btn_row.addStretch()

        self.register_btn = QPushButton(" " + t("admin.btn.register"))
        self.register_btn.setObjectName("registerCandidatesButton")
        self.register_btn.setIcon(_icon("fa5s.link", "#388bfd"))
        self.register_btn.setIconSize(_ICON_SIZE)
        self.register_btn.clicked.connect(self._register_candidates_onchain)
        btn_row.addWidget(self.register_btn)
        layout.addLayout(btn_row)

        self._candidates_log = _make_log_box(2)
        layout.addWidget(self._candidates_log)
        return box

    # ─── Избиратели ────────────────────────────────────────────

    def _build_voters_section(self) -> _VoterDropZone:
        box = _VoterDropZone(t("admin.section.voters_dnd"), self)
        self._sec_voters = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        # ── Создаём все элементы (порядок создания не важен) ──
        self.import_voters_btn = QPushButton(" " + t("admin.btn.import"))
        self.import_voters_btn.setObjectName("iconButton")
        self.import_voters_btn.setIcon(_icon("fa5s.file-import", "#f0883e"))
        self.import_voters_btn.setIconSize(_ICON_SIZE)
        self.import_voters_btn.clicked.connect(self._import_voters)

        self.export_voters_btn = QPushButton(" " + t("admin.btn.export"))
        self.export_voters_btn.setObjectName("iconButton")
        self.export_voters_btn.setIcon(_icon("fa5s.file-export", "#e3b341"))
        self.export_voters_btn.setIconSize(_ICON_SIZE)
        self.export_voters_btn.clicked.connect(self._export_voters)

        self.generate_voters_btn = QPushButton(" " + t("admin.btn.generate_voters"))
        self.generate_voters_btn.setObjectName("iconButton")
        self.generate_voters_btn.setIcon(_icon("fa5s.users", "#f0883e"))
        self.generate_voters_btn.setIconSize(_ICON_SIZE)
        self.generate_voters_btn.clicked.connect(self._generate_voters)

        self._lbl_count = QLabel(t("admin.label.count") + ":")
        self._lbl_count.setObjectName("fieldLabel")

        self.voter_count_spin = QSpinBox()
        self.voter_count_spin.setRange(1, 1000)
        self.voter_count_spin.setValue(10)
        self.voter_count_spin.setFixedWidth(70)

        self.fund_voters_btn = QPushButton(" " + t("admin.btn.fund"))
        self.fund_voters_btn.setObjectName("iconButton")
        self.fund_voters_btn.setIcon(_icon("fa5s.coins", "#e3b341"))
        self.fund_voters_btn.setIconSize(_ICON_SIZE)
        self.fund_voters_btn.setToolTip(t("admin.tooltip.fund_voters"))
        self.fund_voters_btn.clicked.connect(self._fund_voters)

        self._lbl_eth = QLabel(t("admin.label.eth") + ":")
        self._lbl_eth.setObjectName("fieldLabel")

        self.fund_amount_spin = QDoubleSpinBox()
        self.fund_amount_spin.setRange(0.001, 10.0)
        self.fund_amount_spin.setValue(0.01)
        self.fund_amount_spin.setDecimals(4)
        self.fund_amount_spin.setSuffix(" ETH")
        self.fund_amount_spin.setFixedWidth(110)

        self._voters_loaded_label = _make_stat_label(
            t("admin.label.loaded") + ":", "0"
        )
        self._whitelisted_label = _make_stat_label(
            t("admin.label.whitelisted") + ":", "--"
        )
        self._funded_label = _make_stat_label(
            t("admin.label.funded") + ":", "--"
        )

        self.whitelist_btn = QPushButton(" " + t("admin.btn.whitelist"))
        self.whitelist_btn.setObjectName("whitelistButton")
        self.whitelist_btn.setIcon(_icon("fa5s.shield-alt", "#3fb950"))
        self.whitelist_btn.setIconSize(_ICON_SIZE)
        self.whitelist_btn.clicked.connect(self._whitelist_voters)

        # ── Ряд 1: Импорт | Экспорт | Генерация+кол-во | Финансирование+сумма ──
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row1.addWidget(self.import_voters_btn)
        row1.addWidget(self.export_voters_btn)
        row1.addSpacing(16)
        row1.addWidget(self.generate_voters_btn)
        row1.addWidget(self._lbl_count)
        row1.addWidget(self.voter_count_spin)
        row1.addSpacing(16)
        row1.addWidget(self.fund_voters_btn)
        row1.addWidget(self._lbl_eth)
        row1.addWidget(self.fund_amount_spin)
        row1.addStretch()
        layout.addLayout(row1)

        # ── Ряд 2: статистика Загружено | В whitelist | Профинансированы ──
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        row2.addLayout(self._voters_loaded_label[0])
        row2.addLayout(self._whitelisted_label[0])
        row2.addLayout(self._funded_label[0])
        row2.addStretch()
        layout.addLayout(row2)

        # ── Ряд 3: кнопка Whitelist (на всю ширину) ──
        layout.addWidget(self.whitelist_btn)

        # ── Ряд 4: мини-лог ──
        self._voters_log = _make_log_box(3)
        layout.addWidget(self._voters_log)

        return box

    # ─── Стадии ────────────────────────────────────────────────
    def _build_stage_section(self) -> QGroupBox:
        box = QGroupBox(t("admin.section.stage"))
        self._sec_stage = box
        layout = QHBoxLayout(box)
        layout.setSpacing(12)

        self.start_button = QPushButton(" " + t("admin.btn.start_voting"))
        self.start_button.setObjectName("startButton")
        self.start_button.setIcon(_icon("fa5s.play", "#ffffff"))
        self.start_button.setIconSize(_ICON_SIZE)
        self.start_button.clicked.connect(self._start_voting)
        self.start_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        layout.addWidget(self.start_button)

        self.finish_button = QPushButton(" " + t("admin.btn.finish_voting"))
        self.finish_button.setObjectName("finishButton")
        self.finish_button.setIcon(_icon("fa5s.flag-checkered", "#ffffff"))
        self.finish_button.setIconSize(_ICON_SIZE)
        self.finish_button.clicked.connect(self._finish_voting)
        self.finish_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        layout.addWidget(self.finish_button)
        return box

    # ──────────────────────────────────────────────────────────────
    # Обработчик смены стадии (вызывается из MainWindow.stageChanged)
    # ──────────────────────────────────────────────────────────────

    def _lock_candidate_inputs(self, locked: bool) -> None:
        """Блокирует поля кандидатов после регистрации или вне SETUP."""
        self.candidate_name_input.setEnabled(not locked)
        self.candidate_party_input.setEnabled(not locked)
        self.candidate_address_input.setEnabled(not locked)
        self._cand_gen_btn.setEnabled(not locked)
        self._cand_add_btn.setEnabled(not locked)
        self._cand_rm_btn.setEnabled(not locked)
        # Кнопка Register тоже:
        if locked and self._candidates_registered:
            self.register_btn.setEnabled(False)

    def _lock_voter_inputs(self, locked: bool) -> None:
        """Блокирует все операции с избирателями."""
        self.generate_voters_btn.setEnabled(not locked)
        self.import_voters_btn.setEnabled(not locked)
        self.export_voters_btn.setEnabled(not locked)
        self.voter_count_spin.setEnabled(not locked)
        self.fund_voters_btn.setEnabled(not locked)
        self.fund_amount_spin.setEnabled(not locked)
        self.whitelist_btn.setEnabled(not locked)
        # Export разрешён всегда, чтобы можно было сохранить уже сгенерированные

    def _set_pre_deploy_state(self) -> None:
        """
        Состояние до деплоя контракта:
        - кандидаты заблокированы
        - voters заблокированы
        - stage кнопки заблокированы
        - admin key разблокирован
        """
        self._lock_candidate_inputs(True)
        self._lock_voter_inputs(True)
        self.start_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        # Admin key редактируем
        self.admin_key_input.setEnabled(True)

    def on_stage_changed(self, stage_name: str) -> None:
        """Реагирует на смену стадии: блокирует операции, недоступные в текущей стадии."""
        finished = (stage_name == "FINISHED")
        not_setup = (stage_name != "SETUP")

        # Избиратели section: блокируем всё, кроме Export, как только вышли из SETUP
        self.generate_voters_btn.setEnabled(not not_setup)
        self.import_voters_btn.setEnabled(not not_setup)
        self.fund_voters_btn.setEnabled(not not_setup)
        self.whitelist_btn.setEnabled(not not_setup)
        self.voter_count_spin.setEnabled(not not_setup)
        self.fund_amount_spin.setEnabled(not not_setup)

        # Кандидаты: блок если не SETUP ИЛИ уже зарегистрированы
        locked = not_setup or self._candidates_registered
        self._lock_candidate_inputs(locked)

        # Stage buttons
        if finished:
            self.start_button.setEnabled(False)
            self.finish_button.setEnabled(False)
        elif stage_name == "ACTIVE":
            self.start_button.setEnabled(False)
            self.finish_button.setEnabled(True)
        elif stage_name == "SETUP":
            self.start_button.setEnabled(True)
            self.finish_button.setEnabled(False)

        logger.info(
            "AdminTab: stage=%s, voters_locked=%s, candidates_locked=%s",
            stage_name, not_setup, locked,
        )
    # ──────────────────────────────────────────────────────────────
    # Баланс + Fund from Dev
    # ──────────────────────────────────────────────────────────────
    def _refresh_admin_balance(self) -> None:
        """
        Admin балас — короткий, в первом лейбле.
        Dev баланс — во втором лейбле, с префиксом "Dev:".
        решает проблему длинного баланса при маленьком окне.
        """
        key = self.admin_key_input.text().strip()
        if not key:
            admin_text = "--"
        elif not self.controller.validate_private_key(key):
            admin_text = "invalid key"
        else:
            try:
                addr = self.controller.get_address_from_key(key)
                bal = self.controller.get_balance_eth(addr)
                admin_text = f"{bal} ETH"
            except Exception:
                admin_text = "error"

        self._admin_balance_label.setText(admin_text)
        self._admin_balance_label.setToolTip(admin_text)

        if self.controller.is_dev_mode():
            self._fund_dev_btn.setVisible(True)
            try:
                dev_addr = self.controller.get_dev_account_address()
                if dev_addr:
                    dev_bal = self.controller.get_balance_eth(dev_addr)
                    dev_text = f"Dev: {dev_bal} ETH"
                    self._dev_balance_label.setText(dev_text)
                    self._dev_balance_label.setToolTip(dev_text)
                    self._dev_balance_label.setVisible(True)
                    return
            except Exception:
                # Geth not ready yet — show placeholder, keep button
                self._dev_balance_label.setText("Dev: --")
                self._dev_balance_label.setVisible(True)
                return

        self._dev_balance_label.setVisible(False)

    def _fund_admin_from_dev(self) -> None:
        """Асинхронный перевод 100 ETH с dev-аккаунта на admin."""
        if not self.controller.is_dev_mode():
            info_ok(
                self, t("common.warning"), t("err.no_dev_mode"),
            )
            return

        key = self.admin_key_input.text().strip()
        if not key:
            warning_ok(
                self, t("common.validation"),
                t("err.admin_key_required"),
            )
            return

        if not self.controller.validate_private_key(key):
            warning_ok(
                self, t("common.validation"), t("err.invalid_key"),
            )
            return

        try:
            admin_addr = self.controller.get_address_from_key(key)
        except Exception as exc:
            error_ok(self, t("common.error"), str(exc))
            return

        self._fund_dev_btn.setEnabled(False)
        Toast(self, t("admin.toast.dev_funding"), kind="info")

        self._fund_dev_worker = FundFromDevWorker(
            self.controller, admin_addr, amount_eth=100.0,
        )
        self._fund_dev_worker.finished.connect(
            self._on_fund_dev_success
        )
        self._fund_dev_worker.error.connect(
            self._on_fund_dev_error
        )

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._fund_dev_worker)
        self._fund_dev_thread = mw.thread_runner.start_worker(
            self._fund_dev_worker
        )

    def _on_fund_dev_success(self, tx_hash: str) -> None:
        try:
            self._fund_dev_btn.setEnabled(True)
            Toast(self, t("admin.toast.dev_funded"), kind="success")
            self._refresh_admin_balance()
        except Exception:
            pass

    def _on_fund_dev_error(self, error: str) -> None:
        try:
            self._fund_dev_btn.setEnabled(True)
            logger.error("Fund from dev failed: %s", error)
            error_ok(
                self, t("admin.dialog.fund_failed"), str(error)
            )
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────
    # Действия с контрактом
    # ──────────────────────────────────────────────────────────────
    def _toggle_key_visibility(self) -> None:
        if self.admin_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.admin_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._show_key_btn.setIcon(_icon("fa5s.eye-slash", "#58a6ff"))
        else:
            self.admin_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._show_key_btn.setIcon(_icon("fa5s.eye", "#58a6ff"))

    def _deploy_contract(self) -> None:
        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"), t("err.admin_key_required"),
            )
            return

        self.deploy_button.setEnabled(False)
        self._deploy_log.append(t("admin.toast.deploy_compiling"))

        self._deploy_worker = DeployWorker(self.controller, admin_key)
        self._deploy_worker.progress.connect(self._deploy_log.append)
        self._deploy_worker.finished.connect(self._on_deploy_success)
        self._deploy_worker.error.connect(self._on_deploy_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._deploy_worker)
        self._deploy_thread = mw.thread_runner.start_worker(self._deploy_worker)

    def _on_deploy_success(self, address: str) -> None:
        self.deploy_button.setEnabled(False)
        self.contract_addr_label.setText(address)
        self._deploy_log.append(f"Deployed: {address}")
        self._refresh_stage_label()
        self._refresh_admin_balance()

        # Контракт развёрнут — разблокируем то что было pre-deploy
        self._lock_candidate_inputs(False)
        self._lock_voter_inputs(False)
        self.start_button.setEnabled(True)

        # Admin key больше нельзя менять до New Session
        self.admin_key_input.setReadOnly(True)
        self.admin_key_input.setToolTip(
            t("admin.tooltip.key_locked")
        )

        Toast(self, t("admin.toast.deployed"), kind="success")
        mw = self.window()
        if hasattr(mw, "notify_first_deploy"):
            mw.notify_first_deploy()

    def _on_deploy_error(self, error: str) -> None:
        try:
            self.deploy_button.setEnabled(True)
            logger.error("Deploy error: %s", error)
            self._show_actionable_error(t("common.error"), error)
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _refresh_stage_label(self) -> None:
        try:
            stage = self.controller.get_stage()
            self.stage_value_label.setText(stage.name)
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────
    # Кандидаты
    # ──────────────────────────────────────────────────────────────
    def _generate_candidate_address(self) -> None:
        from src.utils.crypto import generate_eth_keypair
        _, address = generate_eth_keypair()
        self.candidate_address_input.setText(address)

    def _add_candidate_to_list(self) -> None:
        name = self.candidate_name_input.text().strip()
        party = self.candidate_party_input.text().strip()
        address = self.candidate_address_input.text().strip()

        if not name or not party or not address:
            warning_ok(
                self, t("common.validation"),
                t("admin.dialog.fields_required"),
            )
            return

        from src.utils.validators import is_valid_eth_address
        if not is_valid_eth_address(address):
            warning_ok(
                self, t("common.validation"),
                t("admin.dialog.invalid_address"),
            )
            return

        existing = [c[2].lower() for c in self._staged_candidates]
        if address.lower() in existing:
            warning_ok(
                self, t("common.validation"),
                t("admin.dialog.duplicate_address"),
            )
            return

        if len(self._staged_candidates) >= 10:
            warning_ok(
                self, t("admin.dialog.candidate_limit"),
                t("admin.dialog.candidate_limit.msg"),
            )
            return

        self._staged_candidates.append((name, party, address))

        row = self.candidates_table.rowCount()
        self.candidates_table.insertRow(row)
        self.candidates_table.setItem(row, 0, _item(name))
        self.candidates_table.setItem(row, 1, _item(party))
        addr_item = _item(address)
        addr_item.setFont(_mono_font())
        self.candidates_table.setItem(row, 2, addr_item)

        self.candidate_name_input.clear()
        self.candidate_party_input.clear()
        self.candidate_address_input.clear()

    def _remove_selected_candidate(self) -> None:
        row = self.candidates_table.currentRow()
        if row < 0:
            return
        self.candidates_table.removeRow(row)
        if row < len(self._staged_candidates):
            self._staged_candidates.pop(row)

    def _register_candidates_onchain(self) -> None:
        if self._candidates_registered:
            info_ok(
                self, t("admin.dialog.already_registered.title"),
                t("admin.dialog.already_registered.msg"),
            )
            return

        if not self._staged_candidates:
            info_ok(
                self, t("admin.dialog.nothing_to_register.title"),
                t("admin.dialog.nothing_to_register.msg"),
            )
            return

        if len(self._staged_candidates) < 2:
            warning_ok(
                self, t("admin.dialog.not_enough_candidates.title"),
                t(
                    "admin.dialog.not_enough_candidates.msg",
                    count=len(self._staged_candidates),
                ),
            )
            return

        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"),
                t("err.admin_key_required"),
            )
            return

        self.register_btn.setEnabled(False)
        self._candidates_log.clear()
        self._candidates_log.append(
            t("admin.toast.registering", count=len(self._staged_candidates))
        )

        from src.ui.workers.register_candidates_worker import (
            RegisterCandidatesWorker,
        )
        self._reg_worker = RegisterCandidatesWorker(
            self.controller, admin_key,
            list(self._staged_candidates),
        )
        self._reg_worker.progress.connect(self._candidates_log.append)
        self._reg_worker.finished.connect(self._on_register_success)
        self._reg_worker.error.connect(self._on_register_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._reg_worker)
        self._reg_thread = mw.thread_runner.start_worker(self._reg_worker)

    def _on_register_success(self, count: int) -> None:
        try: 
            self._candidates_registered = True
            self.register_btn.setEnabled(False)
            self._lock_candidate_inputs(True)
            Toast(
                self,
                t("admin.toast.candidates_registered", count=count),
                kind="success",
            )
            mw = self.window()
            if hasattr(mw, "notify_candidates_registered"):
                mw.notify_candidates_registered()
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _on_register_error(self, error: str) -> None:
        try:  
            self.register_btn.setEnabled(True)
            logger.error("Register error: %s", error)
            self._show_actionable_error(t("common.error"), error)
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    # ──────────────────────────────────────────────────────────────
    # Избиратели
    # ──────────────────────────────────────────────────────────────
    def _generate_voters(self) -> None:
        count = self.voter_count_spin.value()
        try:
            voters = self.controller.generate_voters(count)
            self._voters_loaded_label[1].setText(
                str(len(self.controller.session.voters))
            )
            Toast(
                self,
                t("admin.toast.voters_generated", count=len(voters)),
                kind="success",
            )
        except Exception as exc:
            error_ok(
                self, t("admin.dialog.generation_failed"), str(exc)
            )

    def _import_voters(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, t("admin.btn.import"), "", "JSON (*.json)"
        )
        if not path:
            return
        self._import_voters_from_path(path)

    def _import_voters_from_path(self, path: str) -> None:
        try:
            count = self.controller.import_voters(path)
            self._voters_loaded_label[1].setText(
                str(len(self.controller.session.voters))
            )
            Toast(
                self,
                t("admin.toast.voters_imported", count=count),
                kind="success",
            )
        except Exception as exc:
            error_ok(
                self, t("admin.dialog.import_failed"), str(exc)
            )

    def _export_voters(self) -> None:
        dlg = ConfirmDialog(
            t("dialog.security.title"),
            t("dialog.security.msg"),
            self,
        )
        if dlg.exec() != dlg.DialogCode.Accepted:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, t("admin.btn.export"), "voters.json", "JSON (*.json)",
        )
        if not path:
            return
        try:
            self.controller.export_voters(path)
            Toast(self, t("admin.toast.voters_exported"), kind="warning")
        except Exception as exc:
            error_ok(
                self, t("admin.dialog.export_failed"), str(exc)
            )

    # ──────────────────────────────────────────────────────────────
    # Финансирование избирателей
    # ──────────────────────────────────────────────────────────────
    def _fund_voters(self) -> None:
        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"), t("err.admin_key_required"),
            )
            return

        voters = self.controller.session.voters
        if not voters:
            info_ok(
                self, t("admin.dialog.no_voters.title"), t("err.no_voters"),
            )
            return

        amount_eth = self.fund_amount_spin.value()
        amount_wei = int(amount_eth * 10 ** 18)
        total_eth = amount_eth * len(voters)

        if not question_yn(
            self, t("dialog.confirm_funding.title"),
            t(
                "dialog.confirm_funding.msg",
                amount=f"{amount_eth:.4f}",
                count=len(voters),
                total=f"{total_eth:.4f}",
            ),
        ):
            return

        self.fund_voters_btn.setEnabled(False)
        self._voters_log.append(
            t(
                "admin.toast.funding",
                count=len(voters),
                amount=f"{amount_eth:.4f}",
            )
        )

        addresses = [v.address for v in voters]
        self._fund_worker = FundVotersWorker(
            self.controller, admin_key, addresses, amount_wei,
        )
        self._fund_worker.progress.connect(self._voters_log.append)
        self._fund_worker.finished.connect(self._on_fund_success)
        self._fund_worker.error.connect(self._on_fund_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._fund_worker)
        self._fund_thread = mw.thread_runner.start_worker(self._fund_worker)

    def _on_fund_success(self, count) -> None:
        try:
            self.fund_voters_btn.setEnabled(True)
            self._funded_label[1].setText(str(count))
            self._refresh_admin_balance()
            Toast(
                self,
                t("admin.toast.voters_funded", count=count),
                kind="success",
            )
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _on_fund_error(self, error: str) -> None:
        try:
            self.fund_voters_btn.setEnabled(True)
            logger.error("Fund error: %s", error)
            self._show_actionable_error(t("common.error"), error)
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    # ──────────────────────────────────────────────────────────────
    # Whitelist
    # ──────────────────────────────────────────────────────────────
    def _whitelist_voters(self) -> None:
        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"), t("err.admin_key_required"),
            )
            return

        if not self.controller.session.voters:
            info_ok(
                self, t("admin.dialog.no_voters.title"), t("err.no_voters"),
            )
            return

        self.whitelist_btn.setEnabled(False)
        self._voters_log.append(t("admin.toast.adding_whitelist"))

        self._wl_worker = WhitelistWorker(self.controller, admin_key)
        self._wl_worker.progress.connect(self._voters_log.append)
        self._wl_worker.finished.connect(self._on_whitelist_success)
        self._wl_worker.error.connect(self._on_whitelist_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._wl_worker)
        self._wl_thread = mw.thread_runner.start_worker(self._wl_worker)

    def _on_whitelist_success(self, result: dict) -> None:
        try:
            self._restore_voter_buttons()
            count = result.get("count", 0)
            self._whitelisted_label[1].setText(str(count))
            Toast(
                self, t("admin.toast.whitelist_updated"), kind="success"
            )
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _on_whitelist_error(self, error: str) -> None:
        try:
            self._restore_voter_buttons()
            logger.error("Whitelist error: %s", error)
            self._show_actionable_error(t("common.error"), error)
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _restore_voter_buttons(self) -> None:
        self.whitelist_btn.setEnabled(True)
        self.generate_voters_btn.setEnabled(True)
        self.import_voters_btn.setEnabled(True)
        self.export_voters_btn.setEnabled(True)
        self.fund_voters_btn.setEnabled(True)

    # ──────────────────────────────────────────────────────────────
    # Действия со стадиями
    # ──────────────────────────────────────────────────────────────
    def _start_voting(self) -> None:
        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"), t("err.admin_key_required"),
            )
            return

        # Pre-check: контракт + минимум 2 кандидата + whitelist
        ready, reason_key = self.controller.check_start_voting_ready()
        if not ready:
            count = self.controller.get_candidates_count_onchain()
            warning_ok(
                self,
                t("admin.dialog.cannot_start.title"),
                t(reason_key, count=count),
            )
            return

        self.start_button.setEnabled(False)
        self._stage_worker = StageWorker(self.controller, admin_key, "start")
        self._stage_worker.finished.connect(self._on_start_success)
        self._stage_worker.error.connect(self._on_start_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._stage_worker)
        self._stage_thread = mw.thread_runner.start_worker(self._stage_worker)

    def _on_start_success(self, result) -> None:
        self.start_button.setEnabled(False)
        self._refresh_stage_label()
        Toast(self, t("admin.toast.voting_active"), kind="success")

    def _on_start_error(self, error) -> None:
        self.start_button.setEnabled(True)
        self._show_actionable_error(t("common.error"), error)

    def _finish_voting(self) -> None:
        admin_key = self.admin_key_input.text().strip()
        if not admin_key:
            warning_ok(
                self, t("common.validation"), t("err.admin_key_required"),
            )
            return

        self.finish_button.setEnabled(False)
        self._finish_worker = StageWorker(self.controller, admin_key, "finish")
        self._finish_worker.finished.connect(self._on_finish_success)
        self._finish_worker.error.connect(self._on_finish_error)

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._finish_worker)
        self._finish_thread = mw.thread_runner.start_worker(self._finish_worker)

    def _on_finish_success(self, result) -> None:
        try:
            self.finish_button.setEnabled(False)
            self._refresh_stage_label()
            Toast(self, t("admin.toast.voting_finished"), kind="info")
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    def _on_finish_error(self, error) -> None:
        try:
            self.finish_button.setEnabled(True)
            self._show_actionable_error(t("common.error"), error)
        except Exception as exc:
            logger.error("UI update failed: %s", exc)

    # ──────────────────────────────────────────────────────────────
    def _show_actionable_error(
        self, title: str, error_text: str
    ) -> None:
        parsed = self.controller.parse_rpc_error(error_text)

        message_key = parsed.get("message_key")
        if message_key:
            message = t(message_key)
        else:
            message = parsed.get("raw_message") or error_text

        action_key = parsed.get("action_key")
        action_text = t(action_key) if action_key else None

        dlg = ErrorDialog(
            self,
            title=title,
            message=message,
            action_text=action_text,
        )
        dlg.exec()
        if dlg.action_accepted:
            action_id = parsed.get("action_id")
            if action_id == "fund_account":
                Toast(self, t("admin.toast.use_fund_btn"), kind="info")
            elif action_id == "sync_nonce":
                Toast(self, t("admin.toast.nonce_sync_hint"), kind="info")

    # ──────────────────────────────────────────────────────────────
    def reset_ui(self) -> None:
        self._staged_candidates.clear()
        self._candidates_registered = False
        self.candidates_table.setRowCount(0)
        self.candidate_name_input.clear()
        self.candidate_party_input.clear()
        self.candidate_address_input.clear()
        self.register_btn.setEnabled(True)
        self._lock_candidate_inputs(False)
        self.contract_addr_label.setText("--")
        self.stage_value_label.setText("--")
        self.deploy_button.setEnabled(True)
        self._voters_loaded_label[1].setText("0")
        self._whitelisted_label[1].setText("--")
        self._funded_label[1].setText("--")
        self._admin_balance_label.setText("--")
        self._dev_balance_label.setVisible(False)
        self._restore_voter_buttons()
        self.start_button.setEnabled(True)
        self.finish_button.setEnabled(True)
        self._deploy_log.clear()
        self._candidates_log.clear()
        self._voters_log.clear()
        self._apply_dev_defaults()
        self._set_pre_deploy_state()
        self.admin_key_input.setReadOnly(False)
        self.admin_key_input.setToolTip("")
        logger.info("AdminTab UI reset")

    # ──────────────────────────────────────────────────────────────
    def retranslate_ui(self) -> None:
        if hasattr(self, "_sec_contract"):
            self._sec_contract.setTitle(t("admin.section.contract"))
        if hasattr(self, "_sec_candidates"):
            self._sec_candidates.setTitle(t("admin.section.candidates"))
        if hasattr(self, "_sec_voters"):
            self._sec_voters.setTitle(t("admin.section.voters_dnd"))
        if hasattr(self, "_sec_stage"):
            self._sec_stage.setTitle(t("admin.section.stage"))

        if hasattr(self, "_lbl_admin_key"):
            self._lbl_admin_key.setText(t("admin.label.admin_key").upper())
        if hasattr(self, "_lbl_balance"):
            self._lbl_balance.setText(t("admin.label.balance").upper())
        if hasattr(self, "_lbl_contract_addr"):
            self._lbl_contract_addr.setText(t("admin.label.contract_addr").upper())
        if hasattr(self, "_lbl_current_stage"):
            self._lbl_current_stage.setText(t("admin.label.current_stage").upper())

        self.deploy_button.setText(" " + t("admin.btn.deploy"))
        self._show_key_btn.setToolTip(t("admin.tooltip.show_hide"))
        self._refresh_balance_btn.setToolTip(t("admin.tooltip.refresh_balance"))
        if hasattr(self, "_fund_dev_btn"):
            self._fund_dev_btn.setToolTip(t("admin.tooltip.fund_from_dev"))

        if hasattr(self, "_lbl_name"):
            self._lbl_name.setText(t("admin.label.name").upper())
        if hasattr(self, "_lbl_party"):
            self._lbl_party.setText(t("admin.label.party").upper())
        if hasattr(self, "_lbl_eth_addr"):
            self._lbl_eth_addr.setText(t("admin.label.eth_addr").upper())
        if hasattr(self, "_lbl_cands_list"):
            self._lbl_cands_list.setText(t("admin.label.candidates_list").upper())
        if hasattr(self, "_cand_gen_btn"):
            self._cand_gen_btn.setText(" " + t("admin.btn.generate"))
        if hasattr(self, "_cand_add_btn"):
            self._cand_add_btn.setText(" " + t("admin.btn.add"))
        if hasattr(self, "_cand_rm_btn"):
            self._cand_rm_btn.setText(" " + t("admin.btn.remove"))
        self.register_btn.setText(" " + t("admin.btn.register"))
        self.candidate_name_input.setPlaceholderText(t("admin.placeholder.name"))
        self.candidate_party_input.setPlaceholderText(t("admin.placeholder.party"))

        self.generate_voters_btn.setText(" " + t("admin.btn.generate_voters"))
        self.import_voters_btn.setText(" " + t("admin.btn.import"))
        self.export_voters_btn.setText(" " + t("admin.btn.export"))
        self.fund_voters_btn.setText(" " + t("admin.btn.fund"))
        self.fund_voters_btn.setToolTip(t("admin.tooltip.fund_voters"))
        self.whitelist_btn.setText(" " + t("admin.btn.whitelist"))

        if hasattr(self, "_lbl_count"):
            self._lbl_count.setText(t("admin.label.count") + ":")
        if hasattr(self, "_lbl_eth"):
            self._lbl_eth.setText(t("admin.label.eth") + ":")

        self.start_button.setText(" " + t("admin.btn.start_voting"))
        self.finish_button.setText(" " + t("admin.btn.finish_voting"))


# ──────────────────────────────────────────────────────────────────
def _make_log_box(max_lines: int = 3) -> QTextEdit:
    box = QTextEdit()
    box.setReadOnly(True)
    box.setMaximumHeight(max_lines * 22 + 16)
    box.setObjectName("logBox")
    return box


def _make_table(headers, col_widths, stretch_col=-1, min_height=120):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.setMinimumHeight(min_height)
    table.horizontalHeader().setHighlightSections(False)
    for i, w in enumerate(col_widths):
        if w is not None:
            table.setColumnWidth(i, w)
    if 0 <= stretch_col < len(headers):
        table.horizontalHeader().setSectionResizeMode(
            stretch_col, QHeaderView.ResizeMode.Stretch
        )
    return table


def _item(text: str) -> QTableWidgetItem:
    it = QTableWidgetItem(str(text))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return it


def _mono_font():
    from PyQt6.QtGui import QFont
    return QFont("Consolas", 11)


def _make_stat_label(caption, value):
    row = QHBoxLayout()
    row.setSpacing(4)
    cap = QLabel(caption)
    cap.setObjectName("fieldLabel")
    val = QLabel(value)
    val.setObjectName("statusValue")
    row.addWidget(cap)
    row.addWidget(val)
    return row, val