"""
Toast — всплывающее уведомление с очередью.
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QTimer,
    QSize,
    Qt,
)
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QWidget

try:
    import qtawesome as qta
    _QTA = True
except ImportError:
    _QTA = False


_STYLES: dict[str, tuple[str, str]] = {
    "success": ("#2da44e", "fa5s.check-circle"),
    "error":   ("#cf222e", "fa5s.times-circle"),
    "warning": ("#bf8700", "fa5s.exclamation-triangle"),
    "info":    ("#0969da", "fa5s.info-circle"),
}

_TOAST_DURATION_MS = 2500
_TOAST_GAP_MS = 150


class _ToastManager(QObject):
    """Глобальная очередь тостов: только один на экране одновременно."""

    _instance: Optional["_ToastManager"] = None

    def __init__(self) -> None:
        super().__init__()
        self._queue: deque[tuple[QWidget, str, str]] = deque()
        self._current: Optional["_ToastWidget"] = None

    @classmethod
    def instance(cls) -> "_ToastManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def enqueue(self, parent: QWidget, text: str, kind: str) -> None:
        # Дедуп: не добавлять, если уже показывается или последний в очереди такой же
        if self._current is not None and self._current.text == text:
            return
        if self._queue and self._queue[-1][1] == text:
            return

        self._queue.append((parent, text, kind))
        if self._current is None:
            self._show_next()

    def _show_next(self) -> None:
        if not self._queue:
            self._current = None
            return

        parent, text, kind = self._queue.popleft()

        # Найти контейнер: centralWidget главного окна
        try:
            main_window = parent.window()
        except Exception:
            self._on_done()
            return

        if main_window is None:
            self._on_done()
            return

        container: QWidget = main_window
        if isinstance(main_window, QMainWindow):
            cw = main_window.centralWidget()
            if cw is not None:
                container = cw

        self._current = _ToastWidget(container, text, kind, self._on_done)
        self._current.show_animated()

    def _on_done(self) -> None:
        self._current = None
        QTimer.singleShot(_TOAST_GAP_MS, self._show_next)


class _ToastWidget(QWidget):
    """Виджет тоста как child главного окна (без window flags)."""

    def __init__(
        self,
        container: QWidget,
        text: str,
        kind: str,
        on_closed,
    ) -> None:
        super().__init__(container)
        # Без этого атрибута background-color из stylesheet
        # не применяется к голому QWidget (только к QFrame/наследникам)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.text = text
        self._on_closed = on_closed

        bg, icon_name = _STYLES.get(kind, _STYLES["info"])

        self.setObjectName("toastContainer")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 18, 12)
        layout.setSpacing(12)

        if _QTA:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(
                qta.icon(icon_name, color="#ffffff").pixmap(QSize(20, 20))
            )
            icon_lbl.setFixedSize(22, 22)
            layout.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setMaximumWidth(360)
        layout.addWidget(text_lbl)

        self.setStyleSheet(
            f"#toastContainer {{"
            f"  background-color: {bg};"
            f"  border-radius: 12px;"
            f"  border: none;"
            f"}}"
            f"#toastContainer QLabel {{"
            f"  background: transparent;"
            f"  border: none;"
            f"  color: #ffffff;"
            f"  font-size: 13px;"
            f"  font-weight: 600;"
            f"}}"
        )

        self.setMinimumWidth(240)
        self.setMaximumWidth(420)
        self.adjustSize()

    def show_animated(self) -> None:
        self._reposition()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        self._anim_in = QPropertyAnimation(self, b"windowOpacity")
        self._anim_in.setDuration(220)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_in.start()

        QTimer.singleShot(_TOAST_DURATION_MS, self._fade_out)

    def _reposition(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        pw = parent.width()
        ph = parent.height()
        my_w = self.width()
        my_h = self.height()
        x = pw - my_w - 20
        y = ph - my_h - 20
        self.move(max(x, 10), max(y, 10))

    def _fade_out(self) -> None:
        self._anim_out = QPropertyAnimation(self, b"windowOpacity")
        self._anim_out.setDuration(280)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.finished.connect(self._finalize)
        self._anim_out.start()

    def _finalize(self) -> None:
        try:
            if callable(self._on_closed):
                self._on_closed()
        finally:
            self.close()
            self.deleteLater()


def Toast(parent: QWidget, text: str, kind: str = "info") -> None:
    """
    Совместимая с прежним API функция.
    Запрашивает показ тоста через глобальный _ToastManager.
    """
    if parent is None or not text:
        return
    _ToastManager.instance().enqueue(parent, text, kind)