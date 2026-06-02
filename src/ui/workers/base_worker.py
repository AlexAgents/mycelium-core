"""
Базовый worker для длительных операций.
"""

from PyQt6.QtCore import (
    QObject,
    pyqtSignal,
)


class BaseWorker(QObject):

    finished = pyqtSignal(object)

    error = pyqtSignal(str)

    progress = pyqtSignal(str)