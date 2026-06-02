"""
Reusable confirm dialog.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ConfirmDialog(QDialog):

    def __init__(
        self,
        title: str,
        message: str,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.setWindowTitle(title)

        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        label = QLabel(message)

        label.setWordWrap(True)

        layout.addWidget(label)

        buttons = QHBoxLayout()

        self.confirm_button = QPushButton(
            "Confirm"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.confirm_button.clicked.connect(
            self.accept
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addStretch()

        buttons.addWidget(
            self.confirm_button
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(buttons)