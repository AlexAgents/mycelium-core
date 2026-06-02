"""
Section card widget.
"""

from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class SectionCard(QFrame):

    def __init__(
        self,
        title: str,
    ) -> None:

        super().__init__()

        self.setStyleSheet("""
            QFrame {
                border: 1px solid #444;
                border-radius: 8px;
                padding: 10px;
                margin: 4px;
            }
        """)

        self.layout = QVBoxLayout(self)

        self.title = QLabel(title)

        self.title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 6px;
        """)

        self.layout.addWidget(
            self.title
        )