"""
Вкладка голосования — интерфейс избирателя.
"""
from __future__ import annotations

import json

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False

from src.ui.widgets.error_dialog import ErrorDialog
from src.ui.widgets.msgbox_helpers import (
    error_ok,
    info_ok,
    question_yn,
    warning_ok,
)
from src.ui.widgets.toast import Toast
from src.ui.workers.mass_vote_worker import MassVoteWorker
from src.ui.workers.vote_worker import VoteWorker
from src.ui.workers.voter_status_worker import VoterStatusWorker
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


class VoteTab(QWidget):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller
        self._last_receipt = None
        self._radio_buttons: list[QRadioButton] = []
        self._candidate_containers: list[QWidget] = []
        self._button_group: QButtonGroup | None = None

        # SEC-06 предупреждение — показ один раз за время жизни вкладки
        self._sec06_shown: bool = False

        # Debounce-таймер для запроса статуса
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(
            self._request_voter_status
        )

        # Ссылка на текущий status worker (для отслеживания актуальности)
        self._status_worker: VoterStatusWorker | None = None

        self._build_ui()

    # ──────────────────────────────────────────────────────────────
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

        layout.addWidget(self._build_auth_section())
        layout.addWidget(self._build_candidates_section())
        layout.addWidget(self._build_action_section())
        layout.addWidget(self._build_receipt_section())
        layout.addWidget(self._build_mass_vote_section())
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ─── Аутентификация ────────────────────────────────────────
    def _build_auth_section(self) -> QGroupBox:
        box = QGroupBox(t("vote.section.auth"))
        self._sec_auth = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        self._lbl_priv_key = _field_label(t("vote.label.private_key"))
        layout.addWidget(self._lbl_priv_key)

        key_row = QHBoxLayout()
        key_row.setSpacing(6)

        self.private_key_input = QLineEdit()
        self.private_key_input.setPlaceholderText("0x...")
        self.private_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.private_key_input.textChanged.connect(
            self._on_key_changed
        )
        self.private_key_input.setObjectName("monoLabel")
        key_row.addWidget(self.private_key_input)

        self._show_key_btn = QPushButton()
        self._show_key_btn.setObjectName("iconButton")
        self._show_key_btn.setIcon(
            _icon("fa5s.eye", "#58a6ff")
        )
        self._show_key_btn.setIconSize(_ICON_SIZE)
        self._show_key_btn.setFixedWidth(32)
        self._show_key_btn.clicked.connect(
            self._toggle_key_visibility
        )
        key_row.addWidget(self._show_key_btn)

        self._load_json_btn = QPushButton(" " + t("vote.btn.load_json"))
        self._load_json_btn.setObjectName("iconButton")
        self._load_json_btn.setIcon(_icon("fa5s.file-import", "#f0883e"))
        self._load_json_btn.setIconSize(_ICON_SIZE)
        self._load_json_btn.clicked.connect(self._load_key_from_json)
        key_row.addWidget(self._load_json_btn)

        layout.addLayout(key_row)

        # Сетка статуса
        grid = QHBoxLayout()
        grid.setSpacing(20)

        self._addr_block = _StatusBlock(
            t("vote.label.address"), "--", mono=True
        )
        self._whitelist_block = _StatusBlock(
            t("vote.label.whitelisted"), "--"
        )
        self._voted_block = _StatusBlock(
            t("vote.label.has_voted"), "--"
        )
        self._stage_block = _StatusBlock(
            t("vote.label.stage"), "--"
        )
        self._balance_block = _StatusBlock(
            t("vote.label.balance"), "--"
        )

        for block in (
            self._addr_block, self._whitelist_block,
            self._voted_block, self._stage_block,
            self._balance_block,
        ):
            grid.addLayout(block)
        grid.addStretch()
        layout.addLayout(grid)

        return box

    # ─── Кандидаты ─────────────────────────────────────────────
    def _build_candidates_section(self) -> QGroupBox:
        box = QGroupBox(t("vote.section.candidates"))
        self._sec_cands = box
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        load_row = QHBoxLayout()
        self.load_candidates_btn = QPushButton(
            " " + t("vote.btn.load_candidates")
        )
        self.load_candidates_btn.setObjectName("iconButton")
        self.load_candidates_btn.setIcon(
            _icon("fa5s.sync-alt", "#79c0ff")
        )
        self.load_candidates_btn.setIconSize(_ICON_SIZE)
        self.load_candidates_btn.clicked.connect(
            self._load_candidates
        )
        load_row.addWidget(self.load_candidates_btn)
        load_row.addStretch()
        layout.addLayout(load_row)

        self._candidates_scroll = QScrollArea()
        self._candidates_scroll.setObjectName("candidateScroll")
        self._candidates_scroll.setWidgetResizable(True)
        self._candidates_scroll.setMinimumHeight(120)
        self._candidates_scroll.setMaximumHeight(220)

        self._candidates_widget = QWidget()
        self._candidates_layout = QVBoxLayout(
            self._candidates_widget
        )
        self._candidates_layout.setContentsMargins(4, 4, 4, 4)
        self._candidates_layout.setSpacing(2)

        self._no_candidates_label = QLabel(t("vote.no_candidates"))
        self._no_candidates_label.setObjectName("fieldLabel")
        self._candidates_layout.addWidget(
            self._no_candidates_label
        )
        self._candidates_layout.addStretch()

        self._candidates_scroll.setWidget(
            self._candidates_widget
        )
        layout.addWidget(self._candidates_scroll)
        return box

    # ─── Действие ──────────────────────────────────────────────
    def _build_action_section(self) -> QGroupBox:
        box = QGroupBox(t("vote.section.action"))
        self._sec_action = box
        layout = QVBoxLayout(box)
        layout.setContentsMargins(16, 12, 16, 12)

        self.cast_vote_btn = QPushButton(" " + t("vote.btn.cast_vote"))
        self.cast_vote_btn.setObjectName("whitelistButton")
        self.cast_vote_btn.setIcon(
            _icon("fa5s.vote-yea", "#3fb950")
        )
        self.cast_vote_btn.setIconSize(QSize(18, 18))
        self.cast_vote_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.cast_vote_btn.clicked.connect(self._cast_vote)
        layout.addWidget(self.cast_vote_btn)
        return box

    # ─── Квитанция ─────────────────────────────────────────────
    def _build_receipt_section(self) -> QGroupBox:
        box = QGroupBox(t("vote.section.receipt"))
        self._sec_receipt = box
        layout = QHBoxLayout(box)
        layout.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(8)

        self._lbl_tx_hash = _field_label(t("vote.label.tx_hash"))
        left.addWidget(self._lbl_tx_hash)

        tx_row = QHBoxLayout()
        self.tx_hash_label = QLabel("--")
        self.tx_hash_label.setObjectName("monoLabel")
        self.tx_hash_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.tx_hash_label.setWordWrap(True)
        tx_row.addWidget(self.tx_hash_label, 1)

        self.copy_tx_btn = QPushButton()
        self.copy_tx_btn.setObjectName("iconButton")
        self.copy_tx_btn.setIcon(
            _icon("fa5s.copy", "#79c0ff")
        )
        self.copy_tx_btn.setIconSize(_ICON_SIZE)
        self.copy_tx_btn.setToolTip(t("common.copy"))
        self.copy_tx_btn.setFixedWidth(38)
        self.copy_tx_btn.setEnabled(False)
        self.copy_tx_btn.clicked.connect(self._copy_tx_hash)
        tx_row.addWidget(self.copy_tx_btn)

        left.addLayout(tx_row)

        self.save_qr_btn = QPushButton(" " + t("vote.btn.save_qr"))
        self.save_qr_btn.setObjectName("iconButton")
        self.save_qr_btn.setIcon(
            _icon("fa5s.save", "#58a6ff")
        )
        self.save_qr_btn.setIconSize(_ICON_SIZE)
        self.save_qr_btn.setEnabled(False)
        self.save_qr_btn.clicked.connect(self._save_qr)
        left.addWidget(self.save_qr_btn)
        left.addStretch()

        layout.addLayout(left, 1)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(140, 140)
        self.qr_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.qr_label.setObjectName("monoLabel")
        self.qr_label.setText(t("vote.qr_placeholder"))
        right.addWidget(self.qr_label)
        layout.addLayout(right)

        return box

    # ─── Массовое голосование ───────────────────────────────────
    def _build_mass_vote_section(self) -> QGroupBox:
        box = QGroupBox(t("vote.section.mass"))
        self._sec_mass = box
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        self._mass_desc = QLabel(t("vote.desc.mass"))
        self._mass_desc.setWordWrap(True)
        self._mass_desc.setObjectName("fieldLabel")
        layout.addWidget(self._mass_desc)

        src_row = QHBoxLayout()
        src_row.setSpacing(8)

        self.mass_vote_json_btn = QPushButton(
            " " + t("vote.btn.from_json")
        )
        self.mass_vote_json_btn.setObjectName("iconButton")
        self.mass_vote_json_btn.setIcon(
            _icon("fa5s.file-import", "#f0883e")
        )
        self.mass_vote_json_btn.setIconSize(_ICON_SIZE)
        self.mass_vote_json_btn.clicked.connect(
            self._mass_vote_from_json
        )
        src_row.addWidget(self.mass_vote_json_btn)

        self.mass_vote_session_btn = QPushButton(
            " " + t("vote.btn.from_session")
        )
        self.mass_vote_session_btn.setObjectName("iconButton")
        self.mass_vote_session_btn.setIcon(
            _icon("fa5s.users", "#79c0ff")
        )
        self.mass_vote_session_btn.setIconSize(_ICON_SIZE)
        self.mass_vote_session_btn.clicked.connect(
            self._mass_vote_from_session
        )
        src_row.addWidget(self.mass_vote_session_btn)
        src_row.addStretch()
        layout.addLayout(src_row)

        self._mass_vote_log = _make_log_box(6)
        layout.addWidget(self._mass_vote_log)

        return box

    # ──────────────────────────────────────────────────────────────
    # Логика аутентификации
    # ──────────────────────────────────────────────────────────────
    def _toggle_key_visibility(self) -> None:
        if (
            self.private_key_input.echoMode()
            == QLineEdit.EchoMode.Password
        ):
            self.private_key_input.setEchoMode(
                QLineEdit.EchoMode.Normal
            )
            self._show_key_btn.setIcon(
                _icon("fa5s.eye-slash", "#58a6ff")
            )
        else:
            self.private_key_input.setEchoMode(
                QLineEdit.EchoMode.Password
            )
            self._show_key_btn.setIcon(
                _icon("fa5s.eye", "#58a6ff")
            )

    def _load_key_from_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, t("vote.btn.load_json"), "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "private_key" in data:
                key = data["private_key"]
            elif "voters" in data and data["voters"]:
                key = data["voters"][0].get(
                    "private_key", ""
                )
            else:
                warning_ok(self, t("vote.dialog.parse_error.title"), t("vote.dialog.parse_error.msg"))
                return
            self.private_key_input.setText(key)
            self._show_sec06_warning()
        except Exception as exc:
            error_ok(self, t("vote.dialog.load_failed"), str(exc))

    def _show_sec06_warning(self) -> None:
        """Показ предупреждения один раз за время жизни вкладки."""
        if self._sec06_shown:
            return
        self._sec06_shown = True
        Toast(self, t("vote.toast.sec06_warning"), kind="warning")

    def _on_key_changed(self, text: str) -> None:
        if not text.strip():
            self._clear_voter_status()
            return
        self._show_sec06_warning()
        # debounce: ждём 600мс перед запросом
        self._status_timer.start(600)

    def _check_stage_for_voting(self) -> bool:
        """
        Проверяет, что стадия и контракт позволяют голосовать.
        Возвращает True если можно, False если показан диалог-блокер.
        """
        if not self.controller.session.contract_address:
            warning_ok(
                self,
                t("vote.dialog.stage.title"),
                t("vote.dialog.stage.no_contract"),
            )
            return False

        try:
            stage = self.controller.get_stage()
        except Exception:
            warning_ok(
                self,
                t("vote.dialog.stage.title"),
                t("vote.dialog.stage.no_contract"),
            )
            return False

        if stage.name == "SETUP":
            warning_ok(
                self,
                t("vote.dialog.stage.title"),
                t("vote.dialog.stage.not_started"),
            )
            return False

        if stage.name == "FINISHED":
            warning_ok(
                self,
                t("vote.dialog.stage.title"),
                t("vote.dialog.stage.finished"),
            )
            return False

        try:
            candidates = self.controller.get_candidates()
            if not candidates:
                warning_ok(
                    self,
                    t("vote.dialog.stage.title"),
                    t("vote.dialog.stage.no_candidates"),
                )
                return False
        except Exception:
            pass

        return True

    # ──────────────────────────────────────────────────────────────
    # Статус избирателя — асинхронный запрос через worker
    # ──────────────────────────────────────────────────────────────
    def _request_voter_status(self) -> None:
        """
        Запускает worker для получения статуса избирателя.
        UI не блокируется на время RPC-запросов.
        """
        key = self.private_key_input.text().strip()
        if not key:
            self._clear_voter_status()
            return

        worker = VoterStatusWorker(self.controller, key)
        worker.finished.connect(self._on_voter_status_received)
        worker.error.connect(self._on_voter_status_error)

        mw = self.window()
        if hasattr(mw, "thread_runner"):
            self._status_worker = worker
            mw.thread_runner.start_worker(worker)

    def _on_voter_status_received(self, payload) -> None:
        """
        Обработчик результата. Проверяет актуальность ключа:
        пока worker работал, пользователь мог ввести другой ключ.
        """
        key_used, status = payload
        current_key = self.private_key_input.text().strip()
        if key_used != current_key:
            return  # устарел, игнорируем

        if not status.key_valid:
            self._clear_voter_status()
            return

        # Адрес
        addr = status.address
        self._addr_block.set_value(
            f"{addr[:10]}...{addr[-6:]}", color="#58a6ff"
        )

        # Whitelist
        if status.is_whitelisted is None:
            self._whitelist_block.set_value("--", color="#8b949e")
        else:
            self._whitelist_block.set_value(
                "YES" if status.is_whitelisted else "NO",
                color="#3fb950" if status.is_whitelisted else "#f85149",
            )

        # Has voted
        if status.has_voted is None:
            self._voted_block.set_value("--", color="#8b949e")
        else:
            self._voted_block.set_value(
                "YES" if status.has_voted else "NO",
                color="#f85149" if status.has_voted else "#3fb950",
            )

        # Stage
        if status.stage_name is None:
            self._stage_block.set_value("--", color="#8b949e")
        else:
            colors = {
                "SETUP": "#8b949e",
                "ACTIVE": "#3fb950",
                "FINISHED": "#a78bfa",
            }
            self._stage_block.set_value(
                status.stage_name,
                color=colors.get(status.stage_name, "#8b949e"),
            )

        # Balance
        if status.balance_eth is None:
            self._balance_block.set_value("--", color="#8b949e")
        else:
            self._balance_block.set_value(
                f"{status.balance_eth} ETH", color="#3fb950"
            )

    def _on_voter_status_error(self, error: str) -> None:
        """Тихая обработка — статус просто остаётся пустым."""
        logger.debug("Voter status worker error: %s", error)
        self._clear_voter_status()

    def _clear_voter_status(self) -> None:
        for block in (
            self._addr_block, self._whitelist_block,
            self._voted_block, self._stage_block,
            self._balance_block,
        ):
            block.set_value("--", color="#8b949e")

    # ──────────────────────────────────────────────────────────────
    # Кандидаты
    # ──────────────────────────────────────────────────────────────
    def _clear_candidates_ui(self) -> None:
        for c in self._candidate_containers:
            self._candidates_layout.removeWidget(c)
            c.deleteLater()
        self._candidate_containers.clear()
        self._radio_buttons.clear()
        if self._button_group:
            for btn in self._button_group.buttons():
                self._button_group.removeButton(btn)
        self._button_group = QButtonGroup(self)

    def _load_candidates(self) -> None:
        self._clear_candidates_ui()
        self._no_candidates_label.hide()

        try:
            candidates = self.controller.get_candidates()
        except Exception as exc:
            self._no_candidates_label.setText(
                f"Error: {exc}"
            )
            self._no_candidates_label.show()
            return

        if not candidates:
            self._no_candidates_label.setText(
                t("vote.no_candidates_chain")
            )
            self._no_candidates_label.show()
            return

        for i, c in enumerate(candidates):
            container = QWidget()
            c_layout = QHBoxLayout(container)
            c_layout.setContentsMargins(8, 6, 8, 6)
            c_layout.setSpacing(12)

            rb = QRadioButton()
            rb.setProperty("candidate_address", c.address)
            self._button_group.addButton(rb, i)
            c_layout.addWidget(rb)

            name_lbl = QLabel(c.name)
            name_lbl.setObjectName("sectionHeader")
            name_lbl.setMinimumWidth(160)
            c_layout.addWidget(name_lbl)

            sep = QLabel("|")
            sep.setObjectName("fieldLabel")
            c_layout.addWidget(sep)

            party_lbl = QLabel(c.party)
            party_lbl.setObjectName("fieldLabel")
            party_lbl.setMinimumWidth(140)
            c_layout.addWidget(party_lbl)

            c_layout.addStretch()

            addr_lbl = QLabel(
                f"{c.address[:10]}...{c.address[-6:]}"
            )
            addr_lbl.setObjectName("monoLabel")
            c_layout.addWidget(addr_lbl)

            self._candidates_layout.insertWidget(
                self._candidates_layout.count() - 1,
                container,
            )
            self._candidate_containers.append(container)
            self._radio_buttons.append(rb)

        Toast(
            self,
            t("vote.toast.candidates_loaded", count=len(candidates)),
            kind="success",
        )

    def on_candidates_registered(self) -> None:
        """Auto-load после регистрации в AdminTab."""
        logger.info("VoteTab: auto-loading candidates")
        self._load_candidates()

    # ──────────────────────────────────────────────────────────────
    # Одиночное голосование
    # ──────────────────────────────────────────────────────────────
    def _cast_vote(self) -> None:
        if not self._check_stage_for_voting():
            return

        private_key = self.private_key_input.text().strip()

        candidate_address = (
            self._get_selected_candidate_address()
        )
        if not candidate_address:
            warning_ok(self, t("common.validation"), t("vote.dialog.select_candidate"))
            return

        from src.core.precheck import PrecheckStatus
        result = self.controller.precheck_vote(private_key)

        if result.status == PrecheckStatus.INVALID_KEY:
            warning_ok(
                self, t("common.validation"), t("err.invalid_key"),
            )
            return
        if result.status == PrecheckStatus.NOT_WHITELISTED:
            warning_ok(
                self,
                t("vote.dialog.not_whitelisted.title"),
                t("err.not_whitelisted"),
            )
            return
        if result.status == PrecheckStatus.ALREADY_VOTED:
            warning_ok(
                self,
                t("vote.dialog.already_voted.title"),
                t("err.already_voted"),
            )
            return
        if result.status == PrecheckStatus.INSUFFICIENT_BALANCE:
            warning_ok(
                self,
                t("vote.dialog.insufficient_balance.title"),
                t("err.insufficient_balance"),
            )
            return
        if result.status == PrecheckStatus.NO_CONTRACT:
            pass

        self.cast_vote_btn.setEnabled(False)
        self.cast_vote_btn.setText(" " + t("vote.cast_vote_submitting"))

        self._vote_worker = VoteWorker(
            self.controller, private_key, candidate_address
        )
        self._vote_worker.finished.connect(
            self._on_vote_success
        )
        self._vote_worker.error.connect(
            self._on_vote_error
        )

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._vote_worker)

        self._vote_thread = (
            mw.thread_runner.start_worker(self._vote_worker)
        )

    def _get_selected_candidate_address(self) -> str | None:
        if not self._button_group:
            return None
        checked = self._button_group.checkedButton()
        if not checked:
            return None
        return checked.property("candidate_address")

    def _on_vote_success(self, receipt) -> None:
        self._last_receipt = receipt
        self.cast_vote_btn.setEnabled(True)
        self.cast_vote_btn.setText(" " + t("vote.btn.cast_vote"))
        self.private_key_input.clear()

        self.tx_hash_label.setText(receipt.tx_hash)
        self.copy_tx_btn.setEnabled(True)

        if receipt.qr_bytes:
            px = QPixmap()
            px.loadFromData(receipt.qr_bytes)
            self.qr_label.setPixmap(
                px.scaled(
                    136, 136,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.save_qr_btn.setEnabled(True)

        # Запросить актуальный статус (но ключа уже нет, пусто)
        self._status_timer.start(100)

        Toast(self, t("vote.toast.success"), kind="success")

    def _on_vote_error(self, error: str) -> None:
        self.cast_vote_btn.setEnabled(True)
        self.cast_vote_btn.setText(" " + t("vote.btn.cast_vote"))
        logger.error("Vote error: %s", error)

        parsed = self.controller.parse_rpc_error(error)

        message_key = parsed.get("message_key")
        if message_key:
            message = t(message_key)
        else:
            message = parsed.get("raw_message") or error

        action_key = parsed.get("action_key")
        action_text = t(action_key) if action_key else None

        dlg = ErrorDialog(
            self,
            title=t("vote.dialog.vote_failed"),
            message=message,
            action_text=action_text,
        )
        dlg.exec()

    # ──────────────────────────────────────────────────────────────
    # Массовое голосование
    # ──────────────────────────────────────────────────────────────
    def _mass_vote_from_json(self) -> None:
        if not self._check_stage_for_voting():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, t("vote.dialog.select_voters_json"), "",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            voters = data.get("voters", [])
            if not voters:
                warning_ok(self, t("vote.dialog.empty_file.title"), t("vote.dialog.empty_file.msg"))
                return
        except Exception as exc:
            error_ok(self, t("vote.dialog.load_failed"), str(exc))
            return
        self._start_mass_vote(voters)

    def _mass_vote_from_session(self) -> None:
        if not self._check_stage_for_voting():
            return
        sv = self.controller.session.voters
        if not sv:
            info_ok(self, t("vote.dialog.no_voters.title"), t("vote.dialog.no_voters.session"))
            return
        voters = [
            {"address": v.address, "private_key": v.private_key}
            for v in sv if v.private_key
        ]
        if not voters:
            warning_ok(self, t("vote.dialog.no_keys.title"), t("vote.dialog.no_keys.msg"))
            return
        self._start_mass_vote(voters)

    def _start_mass_vote(self, voters: list[dict]) -> None:
        try:
            candidates = self.controller.get_candidates()
        except Exception as exc:
            error_ok(self, t("common.error"), str(exc))
            return

        if not candidates:
            warning_ok(self, t("vote.dialog.no_candidates.title"), t("err.no_candidates"))
            return

        caddrs = [c.address for c in candidates]

        if not question_yn(
            self,
            t("dialog.confirm_mass_vote.title"),
            t(
                "dialog.confirm_mass_vote.msg",
                voters=len(voters),
                candidates=len(candidates),
            ),
        ):
            return

        self._clear_receipt()

        self.mass_vote_json_btn.setEnabled(False)
        self.mass_vote_session_btn.setEnabled(False)
        self._mass_vote_log.clear()
        self._mass_vote_log.append(
            f"Starting mass vote: {len(voters)} voters..."
        )

        self._mv_worker = MassVoteWorker(
            self.controller, voters, caddrs,
        )
        self._mv_worker.progress.connect(
            self._mass_vote_log.append
        )
        self._mv_worker.finished.connect(
            self._on_mass_vote_success
        )
        self._mv_worker.error.connect(
            self._on_mass_vote_error
        )

        mw = self.window()
        if hasattr(mw, "connect_worker_progress"):
            mw.connect_worker_progress(self._mv_worker)

        self._mv_thread = mw.thread_runner.start_worker(
            self._mv_worker
        )

    def _on_mass_vote_success(self, result: dict) -> None:
        self.mass_vote_json_btn.setEnabled(True)
        self.mass_vote_session_btn.setEnabled(True)
        voted = result.get("voted", 0)
        failed = result.get("failed", 0)
        skipped = (
            result.get("skipped_whitelist", 0)
            + result.get("skipped_balance", 0)
            + result.get("skipped_already_voted", 0)
            + result.get("skipped_no_key", 0)
        )
        kind = "success" if failed == 0 else "warning"
        Toast(
            self,
            t(
                "vote.toast.mass_result",
                voted=voted,
                skipped=skipped,
                failed=failed,
            ),
            kind=kind,
        )

    def _on_mass_vote_error(self, error: str) -> None:
        self.mass_vote_json_btn.setEnabled(True)
        self.mass_vote_session_btn.setEnabled(True)
        logger.error("Mass vote error: %s", error)
        error_ok(self, t("vote.dialog.mass_failed"), error)

    # ──────────────────────────────────────────────────────────────
    # Квитанция
    # ──────────────────────────────────────────────────────────────
    def _copy_tx_hash(self) -> None:
        if self._last_receipt:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(
                self._last_receipt.tx_hash
            )
            Toast(self, t("vote.toast.tx_copied"), kind="info")

    def _save_qr(self) -> None:
        if (
            not self._last_receipt
            or not self._last_receipt.qr_bytes
        ):
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("vote.btn.save_qr"), "receipt.png", "PNG (*.png)"
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(self._last_receipt.qr_bytes)
            Toast(self, t("vote.toast.qr_saved"), kind="success")
        except Exception as exc:
            error_ok(self, t("vote.dialog.save_failed"), str(exc))

    def _clear_receipt(self) -> None:
        """Очистка секции квитанции."""
        self._last_receipt = None
        self.tx_hash_label.setText("--")
        self.copy_tx_btn.setEnabled(False)
        self.save_qr_btn.setEnabled(False)
        self.qr_label.clear()
        self.qr_label.setText(t("vote.qr_placeholder"))

    # ──────────────────────────────────────────────────────────────
    # Сброс
    # ──────────────────────────────────────────────────────────────
    def reset_ui(self) -> None:
        # Сброс локального флага SEC-06
        self._sec06_shown = False

        self.private_key_input.clear()
        self._clear_voter_status()
        self._clear_candidates_ui()
        self._no_candidates_label.setText(
            t("vote.no_candidates")
        )
        self._no_candidates_label.show()
        self._clear_receipt()
        self.cast_vote_btn.setEnabled(True)
        self.cast_vote_btn.setText(" " + t("vote.btn.cast_vote"))
        self.mass_vote_json_btn.setEnabled(True)
        self.mass_vote_session_btn.setEnabled(True)
        self._mass_vote_log.clear()
        logger.info("VoteTab UI reset")

    # ──────────────────────────────────────────────────────────────
    # i18n
    # ──────────────────────────────────────────────────────────────
    def retranslate_ui(self) -> None:
        """Перевод всех статических надписей вкладки."""
        if hasattr(self, "_sec_auth"):
            self._sec_auth.setTitle(t("vote.section.auth"))
        if hasattr(self, "_sec_cands"):
            self._sec_cands.setTitle(t("vote.section.candidates"))
        if hasattr(self, "_sec_action"):
            self._sec_action.setTitle(t("vote.section.action"))
        if hasattr(self, "_sec_receipt"):
            self._sec_receipt.setTitle(t("vote.section.receipt"))
        if hasattr(self, "_sec_mass"):
            self._sec_mass.setTitle(t("vote.section.mass"))

        if hasattr(self, "_lbl_priv_key"):
            self._lbl_priv_key.setText(
                t("vote.label.private_key").upper()
            )
        if hasattr(self, "_lbl_tx_hash"):
            self._lbl_tx_hash.setText(
                t("vote.label.tx_hash").upper()
            )

        self._addr_block.set_caption(t("vote.label.address"))
        self._whitelist_block.set_caption(t("vote.label.whitelisted"))
        self._voted_block.set_caption(t("vote.label.has_voted"))
        self._stage_block.set_caption(t("vote.label.stage"))
        self._balance_block.set_caption(t("vote.label.balance"))

        if hasattr(self, "_load_json_btn"):
            self._load_json_btn.setText(" " + t("vote.btn.load_json"))
        self.load_candidates_btn.setText(
            " " + t("vote.btn.load_candidates")
        )
        self.cast_vote_btn.setText(" " + t("vote.btn.cast_vote"))
        self.save_qr_btn.setText(" " + t("vote.btn.save_qr"))
        self.mass_vote_json_btn.setText(" " + t("vote.btn.from_json"))
        self.mass_vote_session_btn.setText(" " + t("vote.btn.from_session"))

        self.copy_tx_btn.setToolTip(t("common.copy"))

        if hasattr(self, "_mass_desc"):
            self._mass_desc.setText(t("vote.desc.mass"))

        if self.qr_label.pixmap() is None or self.qr_label.pixmap().isNull():
            self.qr_label.setText(t("vote.qr_placeholder"))

        if self._no_candidates_label.isVisible():
            self._no_candidates_label.setText(
                t("vote.no_candidates")
            )


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────
def _make_log_box(max_lines: int = 3) -> QTextEdit:
    box = QTextEdit()
    box.setReadOnly(True)
    box.setMaximumHeight(max_lines * 22 + 16)
    box.setObjectName("logBox")
    return box


class _StatusBlock(QVBoxLayout):
    """
    Блок «подпись + значение» с возможностью смены caption (для i18n).
    """

    def __init__(
        self, caption: str, value: str, *, mono: bool = False
    ) -> None:
        super().__init__()
        self.setSpacing(3)
        self._cap = QLabel(caption.upper())
        self._cap.setObjectName("fieldLabel")
        self.addWidget(self._cap)
        self._val = QLabel(value)
        self._val.setObjectName("statusValue")
        if mono:
            self._val.setObjectName("monoLabel")
            self._val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
        self.addWidget(self._val)

    def set_value(
        self, text: str, *, color: str = "#c9d1d9"
    ) -> None:
        self._val.setText(text)

    def set_caption(self, caption: str) -> None:
        """Обновление подписи (для i18n)."""
        self._cap.setText(caption.upper())