"""
MYCELIUM CORE entrypoint.
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.core.app_controller import AppController
from src.ui.main_window import MainWindow
from src.utils.config import get_app_config
from src.utils.i18n import I18N
from src.utils.logger import setup_logging
from src.utils.paths import ensure_directories
from src.utils.theme_manager import ThemeManager


def main():
    ensure_directories()
    setup_logging()

    cfg = get_app_config()

    qt = QApplication(sys.argv)
    # FIX: язык берётся из app.cfg вместо захардкоженного "ru"
    qt.i18n = I18N(cfg.language)
    qt.theme_manager = ThemeManager(qt)
    qt.theme_manager.apply_theme(cfg.theme)
    qt._theme_mode = cfg.theme

    controller = AppController()
    controller.startup()
    controller.create_session()

    window = MainWindow(controller)
    window.app = qt
    window.show()
    sys.exit(qt.exec())


if __name__ == "__main__":
    main()