"""
Базовый worker для длительных операций.
"""
from PyQt6.QtCore import (
    QObject,
    pyqtSignal,
)


class BaseWorker(QObject):
    """
    Базовый класс для всех фоновых workers.

    Сигналы:
        finished(object)  — результат операции (любой тип)
        error(str)        — текст ошибки
        progress(str)     — текстовое сообщение о прогрессе
        percent(int)      — процент выполнения 0..100 (для progress bar)
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    percent = pyqtSignal(int)